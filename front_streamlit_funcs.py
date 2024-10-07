import hashlib
from datetime import datetime
import asyncpg
from aiocache import Cache
import streamlit as st
from aiocache import cached
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env
SSLMODE= os.getenv('SSLMODE')   #'require'
SSLKEY=  os.getenv('SSLKEY')  #'C:/nginx-1.26.2/ssl/selfsigned.key'
SSLCERT=  os.getenv('SSLCERT')  #'C:/nginx-1.26.2/ssl/selfsigned.crt'
SSLROOTCERT=   os.getenv('SSLROOTCERT') #None

class DatabaseConfig:
    def __init__(self, dbname, user, password, host, port, sslmode, sslrootcert, sslcert, sslkey):
        if sslrootcert!='None':
                 self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}&sslrootcert={sslrootcert}&sslcert={sslcert}&sslkey={sslkey}"
        else:
                 self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}&sslcert={sslcert}&sslkey={sslkey}"

config = DatabaseConfig(
    dbname="postgres",
    user="postgres",
    password="experiment",
    host="localhost",
    port="5432",
    sslmode=SSLMODE,  # No verification needed
    sslrootcert=SSLROOTCERT,   # Not needed
    sslcert=SSLCERT,       # Not needed
    sslkey=SSLKEY         # Not needed
)

cache = Cache.MEMORY 

async def get_pool():
    if 'pool' not in st.session_state:
        st.session_state.pool = await init_pool()
    return st.session_state.pool

#сохранение пула в сессии, чтобы при каждом новом пользователе-подключении не создавать новый пул
@cached(ttl=None, cache=cache)
async def init_pool():
    return await asyncpg.create_pool(
        dsn= config.dsn                           #"postgresql://postgres:experiment@localhost/postgres"
    )
# добавление пользователя
async def add_user(user_email, password):
    pool = await get_pool()
    async with pool.acquire() as conn:
        registration_date = datetime.now()
        password_hash = hashlib.sha256(password.encode()).hexdigest()  # Simple password hashing
        await conn.execute("""
            INSERT INTO yandex_rag_user (user_email, password_hash, token_registration_date)
            VALUES ($1, $2, $3)
        """, user_email, password_hash, registration_date)

# аутентификация пользователя
async def authenticate(user_email, password):
    pool = await get_pool()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT * FROM yandex_rag_user WHERE user_email = $1 AND password_hash = $2
        """, user_email, password_hash)
        return result

# проверка оплаты
async def has_paid(user_email):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT paid FROM yandex_rag_user WHERE user_email = $1
        """, user_email)
        return result['paid'] == 1 if result else False
#  проверка mail
async def mail_exists(user_email):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT * FROM yandex_rag_user WHERE user_email = $1
        """, user_email)
        return result
