import logging

import streamlit as st

from modules.helpers import read_file
from modules.ui import (
    display_link_to_repo,
    display_nav_menu,
)


def main():
    st.set_page_config(
        page_title="YouTube AI", layout="wide", initial_sidebar_state="auto"
    )

    # display sidebar with page links
    display_nav_menu()
    display_link_to_repo()

    st.markdown(body=read_file(".assets/home.md"))


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO,
    )
    main()
