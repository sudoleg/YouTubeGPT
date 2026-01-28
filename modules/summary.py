import logging

import ollama
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .helpers import num_tokens_from_string, read_file

SYSTEM_PROMPT = read_file("prompts/summary_system_prompt.txt")

USER_PROMPT_TEMPLATE = read_file("prompts/summary_user_prompt.txt")

# info about OpenAI's GPTs context windows: https://platform.openai.com/docs/models
OPENAI_CONTEXT_WINDOWS = {
    "gpt-3.5-turbo": {"total": 16385, "output": 4096},
    "gpt-4": {"total": 8192, "output": 4096},
    "gpt-4-turbo": {"total": 128000, "output": 4096},
    "gpt-4o": {"total": 128000, "output": 16384},
    "gpt-4o-mini": {"total": 128000, "output": 16384},
    "gpt-4.1-nano": {"total": 1047576, "output": 32768},
    "gpt-4.1-mini": {"total": 1047576, "output": 32768},
    "gpt-4.1": {"total": 1047576, "output": 32768},
    "gpt-5.1-chat-latest": {"total": 400000, "output": 128000},
    "gpt-5.1": {"total": 400000, "output": 128000},
    "gpt-5.2": {"total": 400000, "output": 128000},
    "gpt-5.2-chat-latest": {"total": 128000, "output": 16384},
    "gpt-5.2-pro": {"total": 400000, "output": 128000},
    "gpt-5-nano": {"total": 400000, "output": 128000},
    "gpt-5-mini": {"total": 400000, "output": 128000},
    "gpt-5": {"total": 400000, "output": 128000},
}


class TranscriptTooLongForModelException(Exception):
    """Raised when the length of the transcript exceeds the context window of a language model."""

    def __init__(self, message, model_name: str):
        self.message = message
        self.model_name = model_name
        super().__init__(self.message)

    def log_error(self):
        # Assuming logging is configured globally
        logging.error("Transcript too long for %s.", self.model_name, exc_info=True)


def get_max_context_length(llm: BaseChatModel) -> int:
    """
    Returns the maximum context length for the provided model.

    Args:
        llm (BaseChatModel): The language model instance.

    Returns:
        int: The maximum context window size in tokens.
    """
    if llm.name not in OPENAI_CONTEXT_WINDOWS.keys():
        model_details = ollama.show(model=llm.name)
        model_info = model_details.get("modelinfo", {})
        general_arch = model_info.get("general.architecture", "")
        return model_info.get(f"{general_arch}.context_length", 4096)
    return OPENAI_CONTEXT_WINDOWS[llm.name]["total"]


def get_transcript_summary(transcript_text: str, llm: BaseChatModel, **kwargs):
    """
    Generates a summary from a video transcript using a language model.

    Args:
        transcript_text (str): The full transcript text of the video.
        llm (BaseChatModel): The language model instance to use for generating the summary.
        **kwargs: Optional keyword arguments.
            - custom_prompt (str): A custom prompt to replace the default summary request.

    Raises:
        TranscriptTooLongForModelException: If the transcript exceeds the model's context window.

    Returns:
        str: The summary/answer in markdown format.
    """

    if "custom_prompt" in kwargs:
        user_prompt = f"""Here is the user's request: {kwargs['custom_prompt']}

        Important style constraint for your answer: 
        - Refer only to "the video" or "this video". 
        - Do not mention transcripts, captions, scraping, or internal processing.

        Content (for your eyes only; do not mention how it was provided):
        ---
        {transcript_text}
        ---
        """
    else:
        user_prompt = USER_PROMPT_TEMPLATE.format(transcript_text=transcript_text)

    max_context_length = get_max_context_length(llm)

    # if the number of tokens in the transcript (plus the number of tokens in the prompt) exceed the model's context window, an exception is raised
    total_tokens = num_tokens_from_string(
        string=user_prompt, model=llm.name
    ) + num_tokens_from_string(string=SYSTEM_PROMPT, model=llm.name)
    if total_tokens > max_context_length:
        raise TranscriptTooLongForModelException(
            message=f"Your transcript exceeds the context window of the chosen model ({llm.name}), which is {max_context_length} tokens. "
            "Consider the following options:\n"
            "1. Choose another model with larger context window.\n"
            "2. Use the 'Chat' feature to ask specific questions about the video. There you won't be limited by the number of tokens.\n\n"
            "You can get more information on context windows for different OpenAI models in the [official documentation](https://platform.openai.com/docs/models).",
            model_name=llm.name,
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    logging.info(
        "Generating summary using model: %s. Total input tokens: %d",
        llm.name,
        total_tokens,
    )
    response = llm.invoke(messages)
    return response.content
