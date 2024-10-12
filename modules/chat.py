from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.documents import Document
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessage

SYSTEM_PROMPT = "You are giong to receive excerpts from an automatically generated video transcript. Your task is to convert every excerpt into structured text. Ensure that the content of the excerpts remains unchanged. Add appropriate punctuation, correct any grammatical errors, remove filler words and divide the text into logical paragraphs, separating them with a single new line. The final output should be in plain text and only include the modified transcript excerpt without any prelude."

user_prompt = HumanMessagePromptTemplate.from_template(
    """Here is part {number} from the original transcript, delimited by ---

    ---
    {transcript_excerpt}
    ---
    """
)


def process_transcript(transcript_excerpts: List[Document], llm: BaseChatModel):
    batch_messages = []
    for num, excerpt in enumerate(transcript_excerpts):
        batch_messages.append(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                user_prompt.format(number=num, transcript_excerpt=excerpt.page_content),
            ]
        )
    response = llm.generate(batch_messages)
    return "\n\n".join(gen[0].text for gen in response.generations)
