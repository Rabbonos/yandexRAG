
#import requests 
from typing import Dict
import aiohttp
#import asyncio

class YandexGPT():
    '''
    model: str - yandexgpt-lite, yandexgpt , custom (понадобится custom_model_id)
    token: str - API key
    folder_id: str - cloud folder id
    custom_model: bool - custom model or not
    custom_model_id: str - custom model id
    '''
    def __init__(self, model:str, token, folder_id, custom_model:bool =False, custom_model_id=None,):    
        #models: yandexgpt-lite, yandexgpt , custom (понадобится custom_model_id)
        self.model = f"gpt://{folder_id}/{model}/latest"
        self.model_custom = f"ds://{custom_model_id}"
        self.token = token
        self.folder_id = folder_id
        self.yandex_gpt_url="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.custom_model=custom_model in (True, 'true', 'True')
        self.yandex_embedding_url = 'https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding'
        self.yandex_embedding =[ f"emb://{folder_id}/text-search-doc/latest" , f"emb://{folder_id}/text-search-query/latest"]

    async def send_request(self, text:str, system_prompt:str, memory: Dict =None,temperature=0.3, max_tokens=2000)->str:
        data = {}
        # Указываем тип модели
        if self.custom_model:
            data["modelUri"] = self.model_custom
        else:
            data["modelUri"] = self.model
        # Настраиваем опции
        data["completionOptions"] = { "stream": False,"temperature": temperature, "maxTokens": max_tokens}
        # Указываем контекст для модели
        data["messages"] = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": f"{text}"},
        ]
        #complete further
        if memory:
                data['messages'].append({'previous messages:': memory})
      
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.yandex_gpt_url,
                        headers={
                            "Accept": "application/json",
                            "Authorization": f"Api-Key  {self.token}",
                            "x-folder-id": self.folder_id }, json=data, ) as response:
                        response = await response.json()

        except Exception as e:
            return f"Error with request to Yandex: {e}"
        
        # результат
        try:
             response= response['result']['alternatives'][0]['message']['text']
             return response
        except Exception as e:
            return f"Error: {response}"
     
    async def get_embedding(self, text: str, embedding_type: str = "doc") -> list:
        
        data = {
            "modelUri": [self.yandex_embedding[0] if embedding_type == "doc" else self.yandex_embedding[1]][0],
            "text": text,
                }
        try:
             
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.yandex_embedding_url,
                        headers={
                            "Accept": "application/json",
                            "Authorization": f"Api-Key  {self.token}",
                            "x-folder-id": self.folder_id
                        },
                        json=data,
                    ) as response:
                    response= await response.json()
        except Exception as e:
            return f"Error with request to Yandex: {e}"
        
        try:
         
            response = response['embedding'] 
            return response
        
        except Exception as e:
            return f"Error: {response}"
        
       
            
# model=YandexGPT("yandexgpt-lite", "AQVNz8LHxHTzJJK68WmpFJiOlyKgbqP8kVEIhd6S", "b1gl42i8kf54i590ma16")        
# # Define an async function to call the YandexGPT methods
# async def main():
#     # Calling async methods with await
#     response = await model.send_request("Как у тебя дела?", "Ты полезный ассистент бот")
#     print(response)
    
#     embedding = await model.get_embedding("Утконос нашёл яйца самки кенгуру", "doc")
#     print(embedding)

# # Running the async function in an event loop
# asyncio.run(main())
