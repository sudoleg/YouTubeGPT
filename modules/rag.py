import logging
import uuid
from typing import List, Literal

from chromadb import Collection
from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from modules.helpers import num_tokens_from_string

CHUNK_SIZE_FOR_UNPROCESSED_TRANSCRIPT = 512

# to provide the LLM with roughly equal amount of input regardless of the chunk size (chosen by the user)
# we define a mapping. So if the user chose to embed chunks with 256 tokens, the model is
# provided with 10 chunks instead of only 3 (like for chunk size of 1024 tokens).
# Thus, the overall amount of input is roughly the same for all chunk sizes (3072 or 2560 tokens)
CHUNK_SIZE_TO_K_MAPPING = {1024: 3, 512: 5, 256: 10, 128: 20}

# TODO: optimize the prompt
RAG_SYSTEM_PROMPT = """You are going to receive excerpts from a video transcript as context. Furthermore, a user will provide a question or a topic.
If you receive a question, give a detailed answer. If you receive a topic, summarize the information on this topic.
In either case, keep your response ground solely in the facts of the context.
If the context does not contain the facts to answer the question, apologize and say that you don't know the answer.
"""

rag_user_prompt_template = """Context: {context}
---
        
Here is the users question/topic: {question}
"""


def split_text_recursively(
    transcript_text: str,
    chunk_size: int = 1024,
    chunk_overlap: int = 0,
    len_func: Literal["characters", "tokens"] = "characters",
):
    """Splits a string recurisively by characters or tokens."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len if len_func == "characters" else num_tokens_from_string,
    )
    splits = text_splitter.create_documents([transcript_text])
    logging.info(
        "Split transcript by %s into %d chunks with a provided chunk size of %d.",
        len_func,
        len(splits),
        chunk_size,
    )
    return splits


def format_docs_for_context(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def embed_excerpts(
    collection: Collection, excerpts: List[Document], embeddings: Embeddings
):
    """If there are no embeddings in the database, each document in the list is embedded in the provided collection."""
    if collection.count() <= 0:
        for e in excerpts:
            response = embeddings.embed_query(e.page_content)
            collection.add(
                ids=[str(uuid.uuid1())],
                embeddings=[response],
                documents=[e.page_content],
            )


def find_relevant_documents(query: str, db: Chroma, k: int = 3):
    """
    Retrieve relevant documents by performing a similarity search.

    Args:
        query (str): The search query.
        db (Chroma): The database to search in.
        k (int): The number of top relevant documents to retrieve. Default is 3.

    Returns:
        List[Document]: A list of the top k relevant documents.
    """

    retriever = db.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(input=query)


def generate_response(
    question: str, llm: BaseChatModel, relevant_docs: List[Document]
) -> str:
    """Generates a response from the LLM based on the question and relevant documents.

    Args:
        question (str): The user's question or topic.
        llm (BaseChatModel): The language model instance to use for generating the response.
        relevant_docs (List[Document]): A list of relevant documents to use as context.

    Returns:
        str: The generated response from the LLM.
    """

    formatted_input = rag_user_prompt_template.format(
        question=question, context=format_docs_for_context(relevant_docs)
    )

    messages = [
        SystemMessage(content=RAG_SYSTEM_PROMPT),
        HumanMessage(content=formatted_input),
    ]

    response = llm.invoke(messages)
    return response.content
