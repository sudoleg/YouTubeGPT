import logging

from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage

from .helpers import num_tokens_from_string

SYSTEM_PROMPT = """
You are going to receive a transcript from a YouTube video. Your task is to process the transcript according to a user's request.

Here are some guidelines for your response:
    - answer in markdown format
    - don't use first level headings
"""

USER_PROMPT_TEMPLATE = """Generate a concise and coherent summary that accurately captures the key points, main topics, and essential information of the video.
        Focus on clarity, relevance, and brevity, ensuring the summary is easy to understand and provides a clear overview of the video’s content.
        The summary should be in whole sentences and contain no more than 300 words.
        Additionaly, extract key insights from the video for contributing to better understanding, emphasizing the main points and providing actionable advise.

        Here is the transcript, delimited by ---

        ---
        {transcript_text}
        ---

        Your response should strictly adhere to this schema:

        ## <short title for the video, consisting of maximum five words>

        <your summary>

        ## Key insights

        <unnumbered list of key insights>
        """

# info about OpenAI's GPTs context windows: https://platform.openai.com/docs/models
CONTEXT_WINDOWS = {
    "gpt-3.5-turbo": {"total": 16385, "output": 4096},
    "gpt-4": {"total": 8192, "output": 4096},
    "gpt-4-turbo": {"total": 128000, "output": 4096},
    "gpt-4o": {"total": 128000, "output": 16384},
    "gpt-4o-mini": {"total": 128000, "output": 16384},
    "gpt-4.1-nano": {"total": 1047576, "output": 32768},
    "gpt-4.1-mini": {"total": 1047576, "output": 32768},
    "gpt-4.1": {"total": 1047576, "output": 32768},
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
        user_prompt = f"""{kwargs['custom_prompt']}

            Here is the transcript, delimited by ---
            ---
            {transcript_text}
            ---
            """
    else:
        user_prompt = USER_PROMPT_TEMPLATE.format(transcript_text=transcript_text)

    # if the number of tokens in the transcript (plus the number of tokens in the prompt) exceed the model's context window, an exception is raised
    if (
        num_tokens_from_string(string=user_prompt, model=llm.model_name)
        + num_tokens_from_string(string=SYSTEM_PROMPT, model=llm.model_name)
        > CONTEXT_WINDOWS[llm.model_name]["total"]
    ):
        raise TranscriptTooLongForModelException(
            message=f"Your transcript exceeds the context window of the chosen model ({llm.model_name}), which is {CONTEXT_WINDOWS[llm.model_name]['total']} tokens. "
            "Consider the following options:\n"
            "1. Choose another model with larger context window (such as gpt-4o).\n"
            "2. Use the 'Chat' feature to ask specific questions about the video. There you won't be limited by the number of tokens.\n\n"
            "You can get more information on context windows for different models in the [official OpenAI documentation about models](https://platform.openai.com/docs/models).",
            model_name=llm.model_name,
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response.content
