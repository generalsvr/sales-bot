from langchain.vectorstores import Chroma
from langchain.schema import Document
from docs import *
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

docs = [
    Document(
        page_content=DOC_1,
    ),
    Document(
        page_content=DOC_2,
    ),
    Document(
        page_content=DOC_3,
    ),
    Document(
        page_content=DOC_4,
    ),
    Document(
        page_content=DOC_5,
    ),
    Document(
        page_content=DOC_6,
    ),
    Document(
        page_content=DOC_7,
    ),
    Document(
        page_content=DOC_8,
    ),
    Document(
        page_content=DOC_9,
    ),
    Document(
        page_content=DOC_10,
    ),
    Document(
        page_content=DOC_11,
    ),
    Document(
        page_content=DOC_12,
    ),
    Document(
        page_content=DOC_13,
    ),
    Document(
        page_content=DOC_14,
    ),
    Document(
        page_content=DOC_15,
    ),
    Document(
        page_content=DOC_16,
    ),
    Document(
        page_content=DOC_17,
    ),
    Document(
        page_content=DOC_18,
    ),
    Document(
        page_content=DOC_19,
    ),
]

db = Chroma.from_documents(docs, embeddings)

def search(query):
    docs = db.similarity_search(query, k=2)
    return docs[0].page_content
