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

outputparser = StrOutputParser()


def get_transcript_summary(transcript: str, llm: ChatOpenAI, **kwargs):
    user_prompt = dedent(
        f"""Summarize the provided video transcript briefly in whole sentences. Prefix your response with a short title for the video, consisting of maximum five words and followed by a hyphen. Answer in plain text format.
                    Here is the transcript, delimited by ---
                    ---
                    {transcript}
                    ---
                    """
    )

    if "custom_prompt" in kwargs:
        user_prompt = dedent(
            f"""{kwargs['custom_prompt']} 
                Answer in plain text format.
                Here is the transcript, delimited by ---
                ---
                {transcript}
                ---
                """
        )
    chain = prompt | llm | outputparser
    return chain.invoke({"input": user_prompt})
