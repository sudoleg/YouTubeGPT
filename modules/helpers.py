import json
import logging
import os
import re
from pathlib import Path
from typing import List, Literal, Optional

import ollama
import openai
import streamlit as st
import tiktoken


def is_api_key_set() -> bool:
    """Checks whether the OpenAI API key is set in streamlit's session state or as environment variable."""
    if os.getenv("OPENAI_API_KEY") or "openai_api_key" in st.session_state:
        return True
    return False


@st.cache_data
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


def get_available_models(
    model_type: Literal["gpts", "embeddings"], api_key: str = ""
) -> List[str]:
    """
    Retrieve a filtered list of available model IDs from OpenAI's API or environment variables, based on the specified model type.

    Args:
        model_type (Literal["gpts", "embeddings"]): The type of models to retrieve, such as 'gpts' or 'embeddings'.
        api_key (str, optional): The API key for authenticating with OpenAI. Defaults to an empty string.

    Returns:
        List[str]: A filtered list of available model IDs matching the specified model type. The list is derived either from the environment variable `AVAILABLE_MODEL_IDS` if set, or from a call to OpenAI's API.
        If an authentication error or any other exception occurs during the API call, an empty list is returned.
    """
    openai.api_key = api_key
    selectable_model_ids = list(
        get_default_config_value(f"available_models.{model_type}")
    )

    def _filter_available(models: List[str]) -> List[str]:
        return [m for m in selectable_model_ids if m in models]

    if not api_key and not os.getenv("OPENAI_API_KEY"):
        return selectable_model_ids

    # AVAILABLE_MODEL_IDS env var stores all the model IDs available to the user as a list (separated by a comma)
    # the env var is set programatically below
    available_model_ids = os.getenv("AVAILABLE_MODEL_IDS")
    if available_model_ids:
        return _filter_available(available_model_ids.split(","))

    try:
        available_model_ids: list = [model.id for model in openai.models.list()]
    except openai.AuthenticationError as e:
        logging.error(
            "An authentication error occurred when fetching available models: %s",
            str(e),
        )
        return []
    except Exception as e:
        logging.error(
            "An unexpected error occurred when fetching available models: %s",
            str(e),
        )
        return []
    else:
        # set the AVAILABLE_MODEL_IDS env var, so that the list of available models
        # doesn't have to be fetched every time
        os.environ["AVAILABLE_MODEL_IDS"] = ",".join(available_model_ids)
        return _filter_available(available_model_ids)


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

    # Log the full path of the saved file
    logging.info("File saved at: %s", file_path)


def get_preferred_languages():
    """Return preferred languages for transcripts."""
    # TODO: return from configuration object or config.json
    return ["en-US", "en", "de"]


# TODO: handle Ollama models as well or fallback to other token count method
def num_tokens_from_string(string: str, model: str = "gpt-4.1-nano") -> int:
    """
    Returns the number of tokens in a text string for OpenAI models.

    Args:
        string (str): The string to count tokens in.
        model (str): Name of the model. Default is 'gpt-4.1-nano'

    See https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    """

    try:
        encoding_name = tiktoken.encoding_name_for_model(model_name=model)
    except KeyError as e:
        logging.error("Couldn't map %s to tokenizer: %s", model, str(e))
        # workaround until https://github.com/openai/tiktoken/issues/395 is fixed
        encoding_name = "o200k_base"

    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))
    except Exception as e:  # pragma: no cover - fallback for offline environments
        logging.error(
            "tiktoken encoding failed (%s). Falling back to whitespace token counting.",
            str(e),
        )
        return len(string.split())


def read_file(file_path: str):
    return Path(file_path).read_text()


def is_environment_prod():
    if os.getenv("ENVIRONMENT") == "production":
        return True
    return False


def get_ollama_host() -> str:
    """Return the configured Ollama host."""
    return os.getenv("OLLAMA_HOST", "http://localhost:11434")


def is_ollama_available(host: Optional[str] = None) -> bool:
    """Checks whether an Ollama server is reachable."""
    ollama_host = host or get_ollama_host()
    try:
        ollama.Client(host=ollama_host).list()
    except Exception as e:
        logging.error("Ollama connection check failed: %s", str(e))
        return False
    return True


def _is_embedding_model(model: dict) -> bool:
    """Determine whether an Ollama model is an embedding model."""
    details = model.get("details", {})
    family = details.get("family", "").lower()
    model_type = details.get("model_type", "").lower()
    name = (model.get("name") or model.get("model") or "").lower()
    return "embed" in family or "embedding" in model_type or "embed" in name


def get_ollama_models(
    model_type: Literal["gpts", "embeddings"], host: Optional[str] = None
) -> List[str]:
    """Returns available Ollama models filtered by type."""
    ollama_host = host or get_ollama_host()
    try:
        models = ollama.Client(host=ollama_host).list().get("models", [])
    except Exception as e:
        logging.error("Could not list Ollama models: %s", str(e))
        return []

    if model_type == "embeddings":
        return [model["model"] for model in models if _is_embedding_model(model)]
    return [model["model"] for model in models if not _is_embedding_model(model)]


def pull_ollama_model(model_name: str, host: Optional[str] = None) -> bool:
    """Triggers pulling an Ollama model; returns True on success."""
    ollama_host = host or get_ollama_host()
    try:
        ollama.Client(host=ollama_host).pull(model=model_name, stream=False)
    except Exception as e:
        logging.error("Failed to pull Ollama model %s: %s", model_name, str(e))
        return False
    return True
