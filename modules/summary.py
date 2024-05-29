import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .helpers import num_tokens_from_string

SYSTEM_PROMPT = "You are a helpful assistant, skilled in processing video transcripts according to user's request. For example this could be summarization, question answering or providing key insights."

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
    ]
)

# info about OpenAI's GPTs context windows: https://platform.openai.com/docs/models
CONTEXT_WINDOWS = {
    "gpt-3.5-turbo": {"total": 16385, "output": 4096},
    "gpt-4": {"total": 8192, "output": 4096},
    "gpt-4-turbo": {"total": 128000, "output": 4096},
    # https://community.openai.com/t/gpt-4o-max-tokens-output-response-length/748822
    "gpt-4o": {"total": 128000, "output": 4096},
}


class TranscriptTooLongForModelException(Exception):
    def __init__(self, message, model_name: str):
        self.message = message
        self.model_name = model_name
        super().__init__(self.message)

    def log_error(self):
        # Assuming logging is configured globally
        logging.error("Transcript too long for %s.", self.model_name, exc_info=True)


def get_transcript_summary(transcript_text: str, llm: ChatOpenAI, **kwargs):
    user_prompt = f"""Based on the provided transcript of the video, create a summary that accurately captures the main topics and arguments. The summray should be in whole sentences and contain no more than 300 words.
        Additionaly, extract key insights from the video for contributing to better understanding, emphasizing the main points and providing actionable advise.
        Here is the transcript, delimited by ---
        ---
        {transcript_text}
        ---
        Answer in markdown format strictly adhering to this schema:

        ## <short title for the video, consisting of maximum five words>

        <your summary>

        ## Key insights

        <unnumbered list of key insights>
        """

    if "custom_prompt" in kwargs:
        user_prompt = f"""{kwargs['custom_prompt']}
            Here is the transcript, delimited by ---
            ---
            {transcript_text}
            ---
            """

    num_tokens_transcript = num_tokens_from_string(transcript_text, "cl100k_base")

    # if the number of transcript tokens exceeds 80% of the context window, an exception is raised
    # here I assume that the size of the summary is around 1/5 of the original transcript
    # my assumption may be wrong. In this case, don't hesitate to start a discussion on github!
    # I would be happy to implement a better solution for the problem of exceeding context widndow
    if num_tokens_transcript >= CONTEXT_WINDOWS[llm.model_name]["total"] * 0.8:
        raise TranscriptTooLongForModelException(
            f"The context window of {llm.model_name} is {CONTEXT_WINDOWS[llm.model_name]['total']} tokens. "
            f"Your transcript has {num_tokens_transcript} tokens, which is more than 80% of the context window. "
            "Assuming that the response is at least 1/5 of the original transcript, the request might fail or you'll get an incomplete summary. "
            "Consider choosing another model with larger context window. "
            "You can get more information on context windows for different models here: https://platform.openai.com/docs/models",
            model_name=llm.model_name,
        )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": user_prompt})
