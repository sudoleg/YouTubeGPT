import logging
from datetime import datetime as dt

import chromadb
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import streamlit as st
from chromadb.config import Settings

from modules.chat import process_transcript
from modules.helpers import (
    num_tokens_from_string,
    save_response_as_file,
    read_file,
    is_environment_prod,
)
from modules.persistance import SQL_DB, Transcript, Video, delete_video
from modules.rag import (
    embed_excerpts,
    split_text_recursively,
    find_relevant_documents,
    generate_response,
)
from modules.ui import (
    GENERAL_ERROR_MESSAGE,
    display_link_to_repo,
    display_missing_api_key_warning,
    display_model_settings,
    display_nav_menu,
    display_video_url_input,
    set_api_key_in_session_state,
)
from modules.youtube import (
    InvalidUrlException,
    NoTranscriptReceivedException,
    extract_youtube_video_id,
    fetch_youtube_transcript,
    get_video_metadata,
)

CHUNK_SIZE_FOR_UNPROCESSED_TRANSCRIPT = 512


st.set_page_config("Chat", layout="wide", initial_sidebar_state="auto")
set_api_key_in_session_state()
display_missing_api_key_warning()

# --- sidebar with model settings ---
display_nav_menu()
display_model_settings()
display_link_to_repo()
# --- end ---

# --- SQLite stuff ---
SQL_DB.connect(reuse_if_open=True)
# create tables if they don't exist
SQL_DB.create_tables([Video, Transcript], safe=True)
# --- end ---

# --- Chroma ---
chroma_connection_established = False
chroma_settings = Settings(allow_reset=True, anonymized_telemetry=False)
try:
    chroma_client = chromadb.HttpClient(
        host="chromadb" if is_environment_prod() else "localhost",
        settings=chroma_settings,
    )
except Exception as e:
    logging.error(e)
    st.warning(
        "Connection to ChromaDB could not be established! You need to have a ChromaDB instance up and running locally on port 8000!"
    )
else:
    chroma_connection_established = True
collection = None
# --- end ---

saved_videos = Video.select()

# create columns
col1, col2 = st.columns([0.5, 0.5], gap="large")


def is_video_selected():
    return True if selected_video_title else False


def display_yt_video_container(url):
    try:
        vid_metadata = get_video_metadata(url)
    except InvalidUrlException as e:
        st.error(e.message)
        e.log_error()
    except Exception as e:
        logging.error("An unexpected error occurred %s", str(e))
        st.error(GENERAL_ERROR_MESSAGE)
    else:
        if vid_metadata:
            st.subheader(
                f"'{vid_metadata['name']}' from {vid_metadata['channel']}.",
                divider="gray",
            )
        st.video(url)


if chroma_connection_established:
    with col1:
        selected_video_title = st.selectbox(
            label="Select from already processed videos",
            placeholder="Choose a video",
            options=[video.title for video in saved_videos],
            index=None,
            key="selected_video",
            help="Once you process a video, it gets saved in a database. You can chat with it at any time, without processing it again! Tip: you may also search for videos by typing (parts of) its title.",
        )
        url_input = display_video_url_input(
            label="Or enter the URL of a new video:", disabled=is_video_selected()
        )

        saved_video = None
        if is_video_selected():
            saved_video = Video.get(Video.title == selected_video_title)

        video_url = ""
        if url_input != "":
            video_url = url_input
        elif is_video_selected():
            video_url = saved_video.link

        if video_url:
            display_yt_video_container(video_url)

        process_button = st.button(
            "Process",
            key="process_button",
            help="This will process the transcript to enable Q&A on the contents.",
            disabled=is_video_selected(),
        )

        if saved_video:
            delete_video_button = st.button(
                label="Delete",
                key="delete_video_button",
                help="Deletes selected video. You won't be able to Q&A this video, unless you process it again!",
            )
            collection = chroma_client.get_or_create_collection(
                name=f"{saved_video.yt_video_id}"
            )
            if delete_video_button:
                try:
                    delete_video(
                        video_title=selected_video_title,
                        chroma_client=chroma_client,
                        collection_name=f"{saved_video.yt_video_id}",
                    )
                except Exception as e:
                    logging.error("An unexpected error occurred %s", str(e))
                    st.error(GENERAL_ERROR_MESSAGE)
                finally:
                    st.info(f"The video '{selected_video_title}' was deleted!")
                    collection = None

        with st.expander("Advanced options"):
            chunk_size = st.number_input(
                label="Chunk size",
                key="chunk_size",
                min_value=128,
                max_value=2048,
                value=1024,
                help="A larger chunk size increases the amount of context provided to the model to answer your question. However, it may be less relevant as with a small chunk size, as smaller chunks can encapsulate more semantic meaning.",
                disabled=is_video_selected(),
            )

            preprocess_checkbox = st.checkbox(
                label="Experimental: enable transcript preprocessing",
                key="preprocessing_checkbox",
                help="By enabling this, the original transcript gets preprocessed. This can greatly improve the results, especially for videos with automatically generated transcripts. However, it results in slightly higher costs, as the whole transcript get's processed by gpt3.5-turbo. Also, the preprocessing will take a substantial amout of time.",
                disabled=is_video_selected(),
            )

        if process_button:
            with st.spinner(
                text="Preparing your video :gear: This can take a little, hang on..."
            ):
                try:
                    # index video
                    video_metadata = get_video_metadata(url_input)

                    # 1. fetch transcript from youtube
                    saved_video = Video.create(
                        yt_video_id=extract_youtube_video_id(url_input),
                        link=url_input,
                        title=video_metadata["name"],
                        channel=video_metadata["channel"],
                        saved_on=dt.now(),
                    )
                    original_transcript = fetch_youtube_transcript(url_input)

                    saved_transcript = Transcript.create(
                        video=saved_video,
                        original_token_num=num_tokens_from_string(original_transcript),
                    )

                    # 2. split the original transcript
                    # if preprocessing is enabled/checked, the chunk size is 512
                    # else the chunk size is determined by the provided value,
                    # which also dafaults to 512
                    original_transcript_excerpts = split_text_recursively(
                        original_transcript,
                        chunk_size=(
                            CHUNK_SIZE_FOR_UNPROCESSED_TRANSCRIPT
                            if preprocess_checkbox
                            else chunk_size
                        ),
                        chunk_overlap=32,
                        len_func="tokens",
                    )

                    collection = chroma_client.get_or_create_collection(
                        name=f"{saved_video.yt_video_id}"
                    )

                    if preprocess_checkbox:
                        # 3. process transcript
                        processed_transcript = process_transcript(
                            transcript_excerpts=original_transcript_excerpts,
                        )
                        save_response_as_file(
                            dir_name="transcripts_processed/",
                            filename=saved_video.title,
                            file_content=processed_transcript,
                        )
                        processed_transcript_excerpts = split_text_recursively(
                            processed_transcript,
                            chunk_size=chunk_size,
                        )
                        Transcript.update(
                            {
                                Transcript.preprocessed: True,
                                Transcript.chunk_size: chunk_size,
                                Transcript.processed_token_num: num_tokens_from_string(
                                    processed_transcript
                                ),
                            }
                        ).where(Transcript.video == saved_video).execute()
                        embed_excerpts(collection, processed_transcript_excerpts)
                    else:
                        Transcript.update(
                            {
                                Transcript.preprocessed: False,
                                Transcript.chunk_size: chunk_size,
                            }
                        ).where(Transcript.video == saved_video).execute()
                        embed_excerpts(collection, original_transcript_excerpts)
                except InvalidUrlException as e:
                    st.error(e.message)
                    e.log_error()
                except NoTranscriptReceivedException as e:
                    st.error(e.message)
                    e.log_error()
                except Exception as e:
                    logging.error(
                        "An unexpected error occurred: %s", str(e), exc_info=True
                    )
                    st.error(GENERAL_ERROR_MESSAGE)
            st.success(
                "The video has been processed! You can refresh the page and choose it in the select-box above."
            )


with col2:
    if collection and collection.count() > 0:

        openai_chat_model = ChatOpenAI(
            api_key=st.session_state.openai_api_key,
            temperature=st.session_state.temperature,
            model=st.session_state.model,
            model_kwargs={"top_p": st.session_state.top_p},
            max_tokens=2048,
        )

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        chroma_db = Chroma(
            client=chroma_client,
            collection_name=collection.name,
            embedding_function=embeddings,
        )

        with st.expander(label=":information_source: Tips and important notes"):
            st.markdown(read_file(".assets/rag_quidelines.md"))

        prompt = st.chat_input(
            placeholder="Ask a question or provide a topic covered in the video",
            key="user_prompt",
        )

        if prompt:
            with st.spinner("Generating answer..."):
                relevant_docs = find_relevant_documents(query=prompt, db=chroma_db)
                response = generate_response(
                    question=prompt, llm=openai_chat_model, relevant_docs=relevant_docs
                )
                st.write(response)