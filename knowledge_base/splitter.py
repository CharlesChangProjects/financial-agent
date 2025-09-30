from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from config.settings import Settings

def get_text_splitter(doc_type: str = "default"):
    if doc_type == "markdown":
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
        return MarkdownHeaderTextSplitter(headers_to_split_on)
    elif doc_type == "semantic":
        return SemanticChunker(OpenAIEmbeddings(model=Settings.EMBEDDING_MODEL))
    else:
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？"]
        )