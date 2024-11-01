import streamlit as st

from modules.persistance import SQL_DB, LibraryEntry, delete_library_entry, Video
from modules.ui import display_nav_menu


st.set_page_config("Library", layout="wide", initial_sidebar_state="auto")
display_nav_menu()

# --- SQLite stuff ---
SQL_DB.connect(reuse_if_open=True)
# create tables if they don't already exist
SQL_DB.create_tables([LibraryEntry], safe=True)
# --- end ---

tab_summaries, tab_answers = st.tabs(["Summaries", "Answers"])


saved_videos = Video.select()


saved_lib_entries_summaries = (
    LibraryEntry.select().where(LibraryEntry.entry_type == "S").execute()
)


def execute_entry_deletion(entry: LibraryEntry):
    """Wrapper func for deleting a library entry."""
    delete_library_entry(entry)
    st.rerun()


with tab_summaries:
    if saved_lib_entries_summaries:
        st.header("Saved summaries")
        for i, entry in enumerate(saved_lib_entries_summaries, 0):
            st.caption(f"{entry.video.title} - {entry.video.channel}")
            with st.expander("Show"):
                st.write(entry.text)
            if st.button(
                label="Delete entry",
                key=f"delete_summary_{i}",
            ):
                execute_entry_deletion(entry)
            st.divider()
    else:
        st.info("You don't have any saved summaries yet!")

with tab_answers:
    selected_video_title = st.selectbox(
        label="Filter by video",
        placeholder="choose a video or start typing",
        # only videos with an associated transcript can be selected
        options=[
            video.title for video in saved_videos if video.transcripts.count() != 0
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
            if st.button(
                label="Delete entry",
                key=f"delete_answer_{j}",
            ):
                execute_entry_deletion(entry)
            st.divider()
    else:
        st.info("You don't have any saved answers yet!")
