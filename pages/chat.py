import streamlit as st

st.set_page_config("Chat", layout="wide", initial_sidebar_state="auto")


col1, col2 = st.columns([0.4, 0.6], gap="large")

with col1:
    st.write("Column for video input and selection area.")

with col2:
    st.write("Column for chat area.")
