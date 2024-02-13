import os
import openai
import langchain
import pinecone

from dotenv import load_dotenv, dotenv_values
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

print("loading files")
text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=2000,
    chunk_overlap=0,
    length_function=len,
)

loader = DirectoryLoader('./data', glob="./dev/*.csv", loader_cls=CSVLoader)
documents = loader.load()

print("splitting files")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
print("done splitting files: ", len(texts), "texts")

# config = {
#     **dotenv_values(".env"),  # load shared development variables
#     **dotenv_values(".env.local"),  # load sensitive variables
#     **os.environ,  # override loaded values with environment variables
# }

load_dotenv(".env.local")

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INDEX_NAME = os.getenv('INDEX_NAME')

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

index = pinecone.Index(INDEX_NAME)
index.describe_index_stats()

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# print("done loading embeddings: ", len(embeddings), "embeddings")

docsearch = Pinecone.from_documents(texts, embeddings, index_name=INDEX_NAME)

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


def parse_response(response):
    print(response['result'])
    print('\n\nSources:')
    for source_name in response["source_documents"]:
        print(source_name.metadata['source'],
              "page #:", source_name.metadata['page'])


retriever = docsearch.as_retriever(
    include_metadata=True, metadata_key='source')

qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type="stuff",
                                       retriever=retriever,
                                       return_source_documents=True)

query = "What is the id of Leiden University in the pdf file."
response = qa_chain(query)

# response = qa_chain(query2)

parse_response(response)
