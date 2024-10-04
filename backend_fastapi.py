#Запускаем докер с базой данных (docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=experiment -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres pgvector/pgvector)
#Потом надо запустить database_setup.py, чтобы создать таблицу в базе данных

#чего нет но возможно должно быть:
# langchain #если удобнее так
# transformers #для бесплатных моделей
# torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121  #для бесплатных моделей
#pytest #для тестов
#good logging #логирование
#caching #для ускорения работы
#add alembic for database migrations #для удобства

#импорты
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends 
from doc_reader import pdf_reader
from database_funcs import get_existing_token, blacklist_token, is_token_blacklisted, cleanup_expired_tokens , get_closest_text, add_token
from yandexrag import YandexGPT
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
import asyncpg #got error with aiopg, this one works fine
from dotenv import load_dotenv
import os
import logging
from text_splitter import CharacterLevelTextSplitter
import asyncio
import jwt  ############################
from pydantic import BaseModel ############################
logging.basicConfig(filename='log.txt',level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s') #конечно так не стоит делать, но пока пойдет
splitter=CharacterLevelTextSplitter()  #инициализация класса для разделения текста на части

#секреты для fastapi
load_dotenv()  # Load environment variables from .env
api_key = os.getenv('API_KEY')
cloud_folder=os.getenv('CLOUD_FOLDER_ID')
SECRET_KEY = os.getenv('SECRET_KEY') 
ALGORITHM =  os.getenv('ALGORITHM') 

#создание пула
async def init_pool():
    return await asyncpg.create_pool(
        dsn="postgresql://postgres:experiment@localhost/postgres"
    )

#тут настройка запуска и закрытия приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # что делаем перед запуском приложения
    app.state.pool = await init_pool()
    app.state.cleanup_task = asyncio.create_task(periodic_cleanup())
    yield
    # что делаем после остановки приложения
    await app.state.pool.close()
    app.state.cleanup_task.cancel()

#создание приложения
app = FastAPI(lifespan=lifespan) #on_startup=[init_pool] - only if we work sycnhronously

#pydantic
class TokenData(BaseModel):
    token:str
    user_email: str =None

    
class TextAcceptor(BaseModel):
    user_email:str =None
    yandex_model:str
    text: str =None
    file: UploadFile = Form(None) #Form and without Form
    embedding_type: str = "doc"
    custom_model: bool = False
    custom_model_id: str = None
    memory: str = None
   

#переодически удаляем старые токены из черного списка
async def periodic_cleanup():
    while True:
        await cleanup_expired_tokens(app)
        await asyncio.sleep(86,400) #раз в день

#декодирование токена
async def decode_jwt(token):
    if await is_token_blacklisted(app ,token):
        return {"error": "Токен был заблокирован"}
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload # mail and expiration date
    
    except jwt.ExpiredSignatureError:
        return {"error": "Токен просрочен"}
    
    except jwt.InvalidTokenError:
        return {"error": "Неверный токен"}
    
async def get_current_user(input:TokenData):
   
   payload = await decode_jwt(input.token)
   
   if "error" in payload:
        raise HTTPException(status_code=403, detail=payload["error"])
   return input

#генерация токена
@app.post("/create_token")
async def generate_token(input: str = Depends(get_current_user)):
    try:
        user_email = input.user_email
        existing_token = await get_existing_token( app , input.user_email)
        
        if existing_token:
            await blacklist_token(app ,existing_token)

        expiration = timedelta(days=30)  # One month expiration
        token_data = {"user_email": input.user_email, "exp":  datetime.now(timezone.utc) + expiration}
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        await add_token(app, access_token, user_email)
        return {'status': 200, "access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        logging.error(f"Error generating token for {user_email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post('/data_accept')
async def text_acceptor(input: TextAcceptor, user_email: str = Depends(get_current_user)):

    try:
            user_email = user_email.user_email 
            model=YandexGPT(input.yandex_model, api_key, cloud_folder, input.custom_model, input.custom_model_id)
            
            if (input.text and input.file) or (not input.text and not input.file):
                          return {"error": "Текст или файл должны быть предоставлены, но не оба."}
            
            if input.file:
                try:
                    pdf_bytes = await input.file.read()  # Read the uploaded file bytes
                    text = pdf_reader(pdf_bytes)
                    text_chunks=  splitter.split_text(text)
                except Exception as e:
                    return {"error": f"Error reading the file: {str(e)}"}
            else:
                try:
                     text_chunks=  splitter.split_text(input.text)
                except Exception as e:
                    return {"error": f"Error splitting the text: {str(e)}"}
                
            async with app.state.pool.acquire() as conn:
                for chunk in text_chunks:
                    # Get embeddings for each chunk
                    embeddings = await model.get_embedding(chunk, input.embedding_type)
                    embeddings = str(embeddings)
                    # Insert data into the database
                    
                    try:
                        await conn.execute("""
                            INSERT INTO yandex_rag_user (user_email, vector_embeddings, text)
                            VALUES ($1, $2, $3)
                        """, user_email, embeddings, chunk)
                    except Exception as e:
                        return {"error": f"Error inserting data into the database: {str(e)}"}
                    
            return  {'status': 200}

    except Exception as e:
        logging.error(f"Error accepting data for {input.user_email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post('/rag_answer', dependencies=[Depends(get_current_user)])
async def rag_answer( input: TextAcceptor, user_email: str = Depends(get_current_user)):
    try:
            
            user_email = user_email.user_email
            
            model=YandexGPT(input.yandex_model, api_key, cloud_folder, input.custom_model, input.custom_model_id)
            
            if (input.text and input.file) or (not input.text and not input.file):
                          return {"error": "Текст или файл должны быть предоставлены, но не оба."}

            if input.file:
                try:
                    pdf_bytes = await input.file.read()  # Read the uploaded file bytes
                    input.text = pdf_reader(pdf_bytes)
                except Exception as e:
                     return {'error': f'Error reading the file: {str(e)}'}
            
            if len(input.text )>2000:
                return {"error": "Текст слишком большой. Текст должен быть меньше 2000 токенов."}
            try:
                embeddings= await model.get_embedding(input.text, input.embedding_type)
                embeddings=str(embeddings)
            except Exception as e:
                 return {"error": f"Error getting embeddings: {str(e)}"}
            try:
                response = await get_closest_text(app ,embeddings, user_email)
                print(response,'response')
                combined_text = ' '.join([result['text']+' ;' for result in response])  
            except Exception as e:
                 return {'error': f"Error getting closest text: {str(e)}"}
            try:
                response = await model.send_request(
                f"Информация в базе данных: {combined_text}\n \
                Вопрос пользователя: {input.text}",\
                "Ты ассистент который отвечает на вопросы исключительно информацией из базы данных",
                memory=input.memory)
            except Exception as e:
                 return {'error': f"Error sending request to Yandex: {str(e)}"}
            #return response from yandexgpt
            return  {'status': 200,'message': response}
    
    except Exception as e:
        logging.error(f"Error generating RAG answer for {input.user_email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__=='__main__':
    pass



#Если надо будет подключить генерация токенов к чему то, то можно будет использовать код снизу
# @app.post("/create_token", dependencies=[Depends(get_current_user)])
# async def generate_token(input: TokenData):
#     try:
#         user_email = input.user_email
#         existing_token = await get_existing_token( app , user_email)
        
#         if existing_token:
#             await blacklist_token(app ,existing_token)

#         expiration = timedelta(days=30)  # One month expiration
#         token_data = {"user_email": user_email, "exp": datetime.utcnow() + expiration}
#         access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

#         return {'status': 200, "access_token": access_token, "token_type": "bearer"}
    
#     except Exception as e:
#         logging.error(f"Error generating token for {user_email}: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")