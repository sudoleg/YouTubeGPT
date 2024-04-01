import logging
from textwrap import dedent

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .helpers import num_tokens_from_string

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant, skilled in processing video transcripts according to user's request. For example this could be summarization, question answering or providing key insights.",
        ),
        ("user", "{input}"),
    ]
)

CONTEXT_WINDOWS = {
    "gpt-3.5-turbo": {"total": 16385, "output": 4096},
    "gpt-4": {"total": 8192, "output": 4096},
    "gpt-4-turbo": {"total": 128000, "output": 4096},
}


class TranscriptTooLongForModelException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def log_error(self):
        # Assuming logging is configured globally
        logging.error("Transcript too long.")


def get_transcript_summary(transcript_text: str, llm: ChatOpenAI, **kwargs):
    user_prompt = dedent(
        f"""The heading should be a single short title for the video, consisting of maximum five words.
        Summarize the provided video transcript briefly in whole sentences. Here is the transcript, delimited by ---
        ---
        {transcript_text}
        ---
        Answer in markdown format strictly adhering to this schema:

        <short title>

        <your summary>
        """
    )

    if "custom_prompt" in kwargs:
        user_prompt = dedent(
            f"""
            {kwargs['custom_prompt']} 
            Here is the transcript, delimited by ---
            ---
            {transcript_text}
            ---
            """
        )

    num_tokens_transcript = num_tokens_from_string(transcript_text, "cl100k_base")

    # if the number of transcript tokens exceeds 80% of the context window, an exception is raised
    # here i assume that the size of the summary is around 1/5 of the original transcript
    # my assumption may be wrong. In this case, don't hesitate to start a discussion on github!
    # I would be happy to implement a better solution for the problem of exceeding context widndow
    if num_tokens_transcript >= CONTEXT_WINDOWS[llm.model_name]["total"] * 0.8:
        raise TranscriptTooLongForModelException(
            f"The context window of {llm.model_name} is {CONTEXT_WINDOWS[llm.model_name]['total']} tokens. "
            f"Your transcript has {num_tokens_transcript} tokens, which is more than 80% of the context window. "
            "Assuming that the response is at least 1/5 of the original transcript, the request might fail or you'll get an incomplete summary. "
            "Consider choosing another model with larger context window. "
            "You can get more information on context windows for different models here: https://platform.openai.com/docs/models"
        )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": user_prompt})
