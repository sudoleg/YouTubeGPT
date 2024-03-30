from textwrap import dedent

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant, skilled in summarizing video transcripts, answering questions based on them and providing key take-aways.",
        ),
        ("user", "{input}"),
    ]
)


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
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": user_prompt})
