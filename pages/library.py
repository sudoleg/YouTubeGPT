from typing import List

import streamlit as st

from modules.persistance import SQL_DB, LibraryEntry, Video, delete_library_entry
from modules.ui import display_download_button, display_nav_menu

st.set_page_config("Library", layout="wide", initial_sidebar_state="auto")
display_nav_menu()

# --- SQLite stuff ---
SQL_DB.connect(reuse_if_open=True)
# create tables if they don't already exist
SQL_DB.create_tables([LibraryEntry], safe=True)
# --- end ---

tab_summaries, tab_answers, tab_export = st.tabs(["Summaries", "Answers", "Export"])
saved_videos = Video.select()


def execute_entry_deletion(entry: LibraryEntry):
    """Wrapper func for deleting a library entry."""
    delete_library_entry(entry)
    st.rerun()


def prepare_entries_for_export(entries: List[LibraryEntry]) -> str:
    """Prepare library entries for export."""
    return "\n\n".join(
        [f"# {entry.question}\n\n{entry.text}\n\n---" for entry in entries]
    )


with tab_summaries:
    selected_channel = st.selectbox(
        label="Filter by channel",
        placeholder="choose a channel or start typing",
        # only videos with an associated transcript can be selected
        options={video.channel for video in saved_videos},
        index=None,
        key="selected_channel",
    )

    if selected_channel:
        saved_lib_entries_summaries = (
            LibraryEntry.select()
            .join(Video)
            .where(LibraryEntry.entry_type == "S", Video.channel == selected_channel)
            .execute()
        )
    else:
        saved_lib_entries_summaries = (
            LibraryEntry.select().where(LibraryEntry.entry_type == "S").execute()
        )

    if saved_lib_entries_summaries:
        st.header("Saved summaries")
        for i, entry in enumerate(saved_lib_entries_summaries, 0):
            st.caption(f"{entry.video.title} - {entry.video.channel}")
            with st.expander("Show"):
                st.write(entry.text)
            display_download_button(data=entry.text, file_name=entry.video.title)
            if st.button(
                label="Delete entry",
                key=f"delete_summary_{i}",
                icon=":material/delete_forever:",
            ):
                execute_entry_deletion(entry)
            st.divider()
    else:
        st.info("You don't have any saved summaries yet!")


with tab_answers:
    selected_video_title = st.selectbox(
        label="Filter by video",
        placeholder="choose a video or start typing",
        # only videos with an associated transcript and library entries can be selected
        options=[
            video.title
            for video in saved_videos
            if (video.transcripts.count() != 0 and video.lib_entries.count() != 0)
        ],
        index=None,
        key="selected_video",
    )

    if selected_video_title:
        saved_lib_entries_answers = (
            LibraryEntry.select()
            .join(Video)
            .where(
                LibraryEntry.entry_type == "A",
                Video.title == st.session_state.selected_video,
            )
            .execute()
        )
    else:
        saved_lib_entries_answers = (
            LibraryEntry.select().where(LibraryEntry.entry_type == "A").execute()
        )

    if saved_lib_entries_answers:
        st.header("Saved answers")
        for j, entry in enumerate(saved_lib_entries_answers, 0):
            st.subheader(entry.question)
            with st.expander("Show"):
                st.write(entry.text)
            display_download_button(
                data="# " + entry.question + "\n\n" + entry.text,
                file_name=entry.question,
            )
            if st.button(
                label="Delete entry",
                key=f"delete_answer_{j}",
            ):
                execute_entry_deletion(entry)
            st.divider()
    else:
        st.info("You don't have any saved answers yet!")


with tab_export:
    st.header("Customize your export")
    st.subheader("Export all answers related to a specific video")
    selected_video_title_for_export = st.selectbox(
        label="Choose video",
        placeholder="choose a video or start typing",
        # only videos with an associated transcript and library entries can be selected
        options=[
            video.title
            for video in saved_videos
            if (video.transcripts.count() != 0 and video.lib_entries.count() != 0)
        ],
        index=None,
        key="selected_video_export",
    )

    saved_lib_entries_answers = (
        LibraryEntry.select()
        .join(Video)
        .where(
            LibraryEntry.entry_type == "A",
            Video.title == st.session_state.selected_video_export,
        )
        .execute()
    )

    if saved_lib_entries_answers:
        with st.expander(
            "Preview rendered markdown export",
        ):
            prepared_data = prepare_entries_for_export(saved_lib_entries_answers)
            st.markdown(prepared_data)

        display_download_button(
            data=prepared_data, file_name=selected_video_title_for_export
        )
