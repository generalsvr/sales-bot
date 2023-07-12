from langchain.vectorstores import Chroma
from langchain.schema import Document
from docs import *
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

docs = [
    Document(
        page_content=DOC_1,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_2,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_3,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_4,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_5,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_6,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_7,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_8,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_9,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_10,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_11,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_12,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_13,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_14,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_15,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_16,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_17,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_18,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
    Document(
        page_content=DOC_19,
        metadata={
            'title': 'The Great Gatsby',
        }
    ),
]

db = Chroma.from_documents(docs, embeddings)

def search(query):
    docs = db.similarity_search(query, k=2)
    return docs[0].page_content
