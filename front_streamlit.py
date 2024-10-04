import streamlit as st
import asyncio
import asyncpg
from threading import Thread
from asyncio import run_coroutine_threadsafe
import os
from datetime import datetime, timedelta, timezone
import jwt
import aiohttp
from front_streamlit_funcs import add_user, authenticate, has_paid, mail_exists

#для генерации токенов
SECRET_KEY = os.getenv('SECRET_KEY') 
ALGORITHM =  os.getenv('ALGORITHM') 
async def generate_temp_token(user_email: str):
    expiration = timedelta(seconds=30)  # 30 seconds expiration
    token_data = {"user_email": user_email, "exp": datetime.now(timezone.utc) + expiration}
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

async def request_token(temp_token:str, user_email:str):
    async with aiohttp.ClientSession() as Session:
            async with Session.post("http://localhost:8000/create_token", json={'user_email':user_email, 'token':temp_token},
                                     headers={"Authorization": f'Bearer {temp_token}', 
                                                 "Content-Type": "application/json"}) as response:
                            response = await response.json()
                            if response.get('status') == 200:
                                access_token = response.get('access_token')
                                return {'status': 200, "access_token": access_token}
                            else:
                                 print(response, temp_token ,user_email )
                                 return {'status': 400, "error": "Token generation failed"}

@st.cache_resource(show_spinner=False)
def create_loop():
    loop = asyncio.new_event_loop()
    thread = Thread(target=loop.run_forever)
    thread.start()
    return loop, thread

st.session_state.event_loop, worker_thread = create_loop()

# Run async tasks in a thread-safe manner
def run_async(coroutine):
    return run_coroutine_threadsafe(coroutine, st.session_state.event_loop).result() #asyncio.get_event_loop()

# главная функция
def main():
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    st.title("Yandex RAG")

    if st.session_state.logged_in:
        st.success(f"Добро пожаловать, {st.session_state.username}!")

        # проверка оплаты
    
        if run_async(has_paid(st.session_state.username)):
            st.info("Доступ к генерации токенов разрешен.")
            if st.button("Сгенерировать токен"):
           
                temp_token= run_async(generate_temp_token(st.session_state.username))
                #request to backend to get token
           
                access_token = run_async(request_token(temp_token, st.session_state.username))
                
                if access_token['status']==200:
                    st.write(f"Ваш токен: {access_token}, используйте его для запросов")
                  
                else:
                    st.write(f"{access_token}")

        else:
            st.warning("У вас нет доступа к генерации токенов. Пожалуйста, свяжитесь с администратором для оплаты.")
            if st.button("Купить доступ"):
                st.write("Покупка доступа пока не подключена")
            
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun() #не лучшее решение, но пока так

    else:
        # меню
        menu = ["Войти", "Зрегистрироваться"]
        choice = st.sidebar.selectbox("Menu", menu)
        st.image('ragyandeximg.png')  #картинка

        if choice == "Зрегистрироваться":
            st.subheader("Создать аккаунт")
            new_user = st.text_input("Email")
            new_password = st.text_input("Пароль", type='password')
            if st.button("Зрегистрироваться"):
                if new_user and new_password:
                    if run_async(mail_exists(new_user)):
                        st.error("Пользователь с таким email уже существует.")
                        return 
                    run_async(add_user(new_user, new_password))
                    st.success("Вы успешно создали аккаунт.")
                    st.info("Следуйте в меню входа для входа.")
                else:
                    st.error("Пожалуйста, укажите email и пароль.")

        elif choice == "Войти":
            st.subheader("Войти")
            username = st.text_input("Email")
            password = st.text_input("Пароль", type='password')
            if st.button("Войти"):
                user = run_async(authenticate(username, password))
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Добро пожаловать, {username}!")
                    st.rerun() #не лучшее решение, но пока так
                else:
                    st.error("неверные учетные данные")

if __name__ == '__main__':
    main()
