import os
import pinecone
import openai
import json

from decouple import config


pinecone.init(
    api_key='6e382f31-8e3d-4499-b289-b2b0bc72d103',
    environment='us-west4-gcp-free'
)

index_name = 'profile-db'
index = pinecone.Index(index_name)

openai.api_key = config('OPENAI_API_KEY') or 'OPENAI_API_KEY'

f = open('model/profile.json')
data = json.load(f)
f.close()

print('data', data)
