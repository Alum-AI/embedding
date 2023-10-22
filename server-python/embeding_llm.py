import os
import openai
import langchain
import pinecone
import json

from dotenv import load_dotenv, dotenv_values
from langchain.document_loaders import DirectoryLoader, TextLoader, UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader
from langchain.vectorstores import FAISS


print("loading files")
text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=2000,
    chunk_overlap=0,
    length_function=len,
)

loader = DirectoryLoader('./data', glob="./prod/*.pdf", loader_cls=PyPDFLoader)
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
index_name = os.getenv('INDEX_NAME')

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

index = pinecone.Index(index_name)
print('describe_index_stats', index.describe_index_stats())

embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# print("done loading embeddings: ", embeddings, "embeddings")


db = Pinecone.from_existing_index(index_name=index_name, embedding=embedding)
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
db = FAISS.from_documents(documents, embedding)
prompt = """
Based on the resume in the pdf files, acocorign to my profile

    ```
    Geroge Washington High School
    Intreated in: Computer, Art, Science
    Targeting Career in: Scientist
    Targeted location in: California
    ```

    suggestion schools?
"""
response = db.similarity_search(prompt)

# json_formatted_str = json.dumps(docs_dict, indent=2)
docs_dict = [{"page_content": doc.page_content,
              "metadata": doc.metadata} for doc in response]
response_docs = json.dumps(docs_dict, indent=2)

print(response_docs)

prompt_template = "```{schools}``` ```{prompt}``` Generate the school list and future salary for each school."

llm = OpenAI(temperature=0)
llm_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(prompt_template)
)


print(llm_chain.predict(schools=response_docs, prompt=prompt))
