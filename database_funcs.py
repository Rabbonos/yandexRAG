from fastapi import FastAPI
#получение токена из базы данных
async def get_existing_token(app: FastAPI ,username: str):
    async with app.state.pool.acquire() as conn:
        # Fetch the existing token for the user
        token = await conn.fetchval(
            '''SELECT token FROM yandex_rag_user WHERE user_email = $1''',
            username
        )
    return token

#добавление токена в черный список
async def blacklist_token(app: FastAPI ,token: str):
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO black_listed_tokens (token) VALUES ($1) ON CONFLICT (token) DO NOTHING''',
            token
        )

#проверка на то, что токен в черном списке
async def is_token_blacklisted(app: FastAPI ,token: str) -> bool:
    async with app.state.pool.acquire() as conn:
        # Check if the token exists in the blacklist
        blacklisted = await conn.fetchval(
            '''SELECT EXISTS (SELECT 1 FROM black_listed_tokens WHERE token = $1)''',
            token
        )
    return blacklisted

#удаление старых токенов
async def cleanup_expired_tokens(app: FastAPI):
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            '''DELETE FROM black_listed_tokens
               WHERE token IN (SELECT token FROM yandex_rag_user WHERE token_registration_date < NOW() - INTERVAL '1 month')'''
        )

#получаем самый близкий текст
async def get_closest_text(app: FastAPI ,embeddings, user_email):
        async with app.state.pool.acquire() as conn:
        
            results = await conn.fetch("""
                SELECT id, text, user_email, 1 - (vector_embeddings <=> $1::vector) AS cosine_similarity
                FROM yandex_rag_user
                WHERE user_email = $2 AND vector_embeddings IS NOT NULL
                ORDER BY cosine_similarity DESC
                LIMIT 5
            """, embeddings, user_email)
                    
            response = []
            for result in results:
                response.append({
                    "id": result["id"],
                    "text": result["text"],
                    "cosine_similarity": result["cosine_similarity"]
                })
        return response

#добавление токена в базу данных 
async def add_token(app: FastAPI, token: str, user_email: str):
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            '''UPDATE yandex_rag_user 
               SET token = $1 
               WHERE user_email = $2 AND password_hash IS NOT NULL''',
            token, user_email,
        )