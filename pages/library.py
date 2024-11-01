import streamlit as st

from modules.persistance import SQL_DB, LibraryEntry, delete_library_entry
from modules.ui import display_nav_menu


st.set_page_config("Library", layout="wide", initial_sidebar_state="auto")
display_nav_menu()

# --- SQLite stuff ---
SQL_DB.connect(reuse_if_open=True)
# create tables if they don't already exist
SQL_DB.create_tables([LibraryEntry], safe=True)
# --- end ---

saved_lib_entries_summaries = (
    LibraryEntry.select().where(LibraryEntry.entry_type == "S").execute()
)
saved_lib_entries_answers = (
    LibraryEntry.select().where(LibraryEntry.entry_type == "A").execute()
)


def execute_entry_deletion(entry: LibraryEntry):
    """Wrapper func for deleting a library entry."""
    delete_library_entry(entry)
    st.rerun()


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
