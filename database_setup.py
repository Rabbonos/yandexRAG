# docker + postqresql(pgvector) + dbeaver
import psycopg2
#from transformers import AutoTokenizer, AutoModel
#import torch
#import numpy as np

# Load pre-trained model and tokenizer
# model_name = "sentence-transformers/all-MiniLM-L6-v2"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModel.from_pretrained(model_name)

# def get_embedding(text):
#     inputs = tokenizer(text, return_tensors="pt")
#     with torch.no_grad():
#         outputs = model(**inputs)
#     embeddings = outputs.last_hidden_state.mean(dim=1).squeeze() #take the last hidden layer ( which is not output layer, not linear ) and take the mean of all the token embeddings
#     return embeddings.numpy().tolist()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="experiment",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector") #one-time initialization of the extension

# Create table with vector column if it doesn't exist
#Create table for user data
cur.execute('''CREATE TABLE IF NOT EXISTS yandex_rag_user (
    id SERIAL PRIMARY KEY,
    user_email TEXT DEFAULT NULL,          -- App user ID
    token_registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- token creation date (need if token is temporary)
    password_hash TEXT DEFAULT NULL,          -- password hash
    text TEXT DEFAULT NULL,           -- text input
    vector_embeddings VECTOR(256) DEFAULT NULL,    -- Vector embeddings , 256 for yandex_embedding model
    paid INTEGER DEFAULT 0           -- Payment status (0 = unpaid, 1 = paid)
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS black_listed_tokens (
    token TEXT PRIMARY KEY          -- token
            
);''')

cur.execute('''CREATE INDEX IF NOT EXISTS idx_user_email ON yandex_rag_user(user_email);''')

conn.commit()
# Clean up
cur.close()
conn.close()