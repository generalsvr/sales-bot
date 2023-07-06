from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from docs import *

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
    )
]

db = Chroma.from_documents(docs, embeddings)

def search(query):
    docs = db.similarity_search(query, k=1)
    print(docs[0])
    return docs[0].page_content