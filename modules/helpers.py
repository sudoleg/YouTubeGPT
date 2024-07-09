import json
import logging
import os
import re
from pathlib import Path
from typing import Union

import openai
import streamlit as st
import tiktoken
from chromadb import HttpClient
from chromadb.config import Settings


def is_api_key_set() -> bool:
    """Checks whether the OpenAI API key is set in streamlit's session state or as environment variable."""
    if os.getenv("OPENAI_API_KEY") or "openai_api_key" in st.session_state:
        return True
    return False


def is_api_key_valid(api_key: str):
    """
    Checks the validity of an OpenAI API key.

    Args:
        api_key (str): The OpenAI API key to be validated.

    Returns:
        bool: True if the API key is valid, False if the API key is invalid.
    """
    openai.api_key = api_key
    try:
        openai.models.list()
    except openai.AuthenticationError as e:
        logging.error(
            "An authentication error occurred when checking API key validity: %s",
            str(e),
        )
        return False
    except Exception as e:
        logging.error(
            "An unexpected error occurred when checking API key validity: %s",
            str(e),
        )
        return False
    else:
        logging.info("API key validation successful")
        return True


def is_environment_prod():
    if os.getenv("ENVIRONMENT") == "production":
        return True
    return False


def establish_chroma_connection() -> Union[HttpClient, None]:
    """
    Establishes and returns a connection to the Chroma database using HttpClient.

    The connection settings include allowing reset and disabling anonymized telemetry.
    The host is set to "chromadb" for production environments, otherwise "localhost".

    Returns:
        HttpClient: An instance of HttpClient if the connection is successful.
        None: If an exception occurs during the connection attempt.
    """
    chroma_settings = Settings(allow_reset=True, anonymized_telemetry=False)
    try:
        chroma_client = HttpClient(
            host="chromadb" if is_environment_prod() else "localhost",
            settings=chroma_settings,
        )
    except Exception as e:
        logging.error(e)
        return None
    else:
        return chroma_client


def get_default_config_value(
    key_path: str,
    config_file_path: str = "./config.json",
) -> str:
    """
    Retrieves a configuration value from a JSON file using a specified key path.

    Args:
        config_file_path (str): A string representing the relative path to the JSON config file.

        key_path (str): A string representing the path to the desired value within the nested JSON structure,
                        with each level separated by a '.' (e.g., "level1.level2.key").


    Returns:
        The value corresponding to the key path within the configuration file. If the key path does not exist,
        a KeyError is raised.

    Raises:
        KeyError: If the specified key path is not found in the configuration.
    """
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

        keys = key_path.split(".")
        value = config
        for key in keys:
            value = value[key]  # Navigate through each level

        return value


def extract_youtube_video_id(url: str):
    """
    Extracts the video ID from a given YouTube URL.

    The function supports various YouTube URL formats including standard watch URLs, short URLs, and embed URLs.

    Args:
        url (str): The YouTube URL from which the video ID is to be extracted.

    Returns:
        str or None: The extracted video ID as a string if the URL is valid and the video ID is found, otherwise None.

    Example:
        >>> extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_youtube_video_id("This is not a valid YouTube URL")
        None

    Note:
        This function uses regular expressions to match the URL pattern and extract the video ID. It is designed to
        accommodate most common YouTube URL formats, but may not cover all possible variations.
    """
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def save_response_as_file(
    dir_name: str, filename: str, file_content, content_type: str = "text"
):
    """
    Saves given content to a file in the specified directory, formatted as either plain text, JSON, or Markdown.

    Args:
        dir_name (str): The directory where the file will be saved.
        filename (str): The name of the file without extension.
        file_content: The content to be saved. Can be a string for text or Markdown, or a dictionary/list for JSON.
        content_type (str): The type of content: "text" for plain text, "json" for JSON format, or "markdown" for Markdown format. Defaults to "text".

    The function creates the directory if it doesn't exist. It saves `file_content` in a file named `filename`
    within that directory, adding the appropriate extension (.txt for plain text, .json for JSON, .md for Markdown) based on `content_type`.
    """

    # Sanitize the filename by replacing slashes with underscores
    filename = filename.replace("/", "_").replace("\\", "_")

    # Create the directory if it does not exist
    os.makedirs(dir_name, exist_ok=True)

    # Adjust the filename extension based on the content type
    extensions = {"text": ".txt", "json": ".json", "markdown": ".md"}
    file_extension = extensions.get(content_type, ".txt")
    filename += file_extension

    # Construct the full path for the file
    file_path = os.path.join(dir_name, filename)

    # Write the content to the file, formatting it according to the content type
    with open(file_path, "w", encoding="utf-8") as file:
        if content_type == "json":
            json.dump(file_content, file, indent=4)
        else:
            file.write(file_content)


def get_preffered_languages():
    # TODO: return from configuration object or config.json
    return ["en-US", "en", "de"]


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """
    Returns the number of tokens in a text string.

    Args:
        string (str): The string to count tokens in.
        encoding_name (str): Encodings specify how text is converted into tokens. Different models use different encodings. Default is cl100k_base, which is used by gpt-3.5 and gpt-4 (turbo).


    Learn more ebout encodings at https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken#encodings
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))


def read_file(file_path: str):
    return Path(file_path).read_text()
