import os
import pinecone
import json

from dotenv import load_dotenv, dotenv_values
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS, Pinecone, Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
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
# print('describe_index_stats', index.describe_index_stats())

embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# print("done loading embeddings: ", embeddings, "embeddings")

db = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding=embedding)
docs_dict = [{"page_content": doc.page_content,
              "metadata": doc.metadata} for doc in documents]
retriever = db.as_retriever()

# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=None,
#     return_source_documents=True
# )

# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=retriever,
#     return_source_documents=True)


# response = qa_chain(query)

# response = llm_chain(prompt)

# print(qa_chain("Tell me who is Alieen-Zhang"))
# db = Chroma.from_documents(documents, embedding)
# prompt = """
# I am looking for universities with Bachelors in Mechanical engineering in 25000 dollars and IELTS 6.5
# """
# response = db.similarity_search(prompt)

# json_formatted_str = json.dumps(docs_dict, indent=2)
# docs_dict = [{"page_content": doc.page_content,
#               "metadata": doc.metadata} for doc in response]
# response_docs = json.dumps(docs_dict, indent=2)

# print(response_docs)

llm = OpenAI(temperature=0)

qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type="stuff",
                                       retriever=retriever,
                                       return_source_documents=True)

# query = "What is the id of Leiden University in the pdf file."
query = "I am looking for universities with Bachelors in Mechanical engineering in 25000 dollars and IELTS 6.5"
response = qa_chain(query)
print(response['result'])
