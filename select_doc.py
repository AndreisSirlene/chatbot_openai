from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))
model = "gpt-4"

products = carrega('data/products.txt')
ecostore_data = carrega('data/ecostore_data.txt')
privacy = carrega('data/privacy.txt')

def select_doc(resposta_openai):
    if "privacy" in resposta_openai:
        return ecostore_data + "\n" + privacy
    elif "products" in resposta_openai:
        return ecostore_data + "\n" + products
    else:
        return ecostore_data 
    
    
def select_contexto(mensagem_usuario):
    prompt_sistema = f"""
    EcoMart has three main documents that detail different aspects of the business:

    #Document 1 "\n {products} "\n"
    #Document 2 "\n" {ecostore_data} "\n"
    #Document 3 "\n" {privacy} "\n"

    Evaluate the user's prompt and return the most appropriate document to be used in the context of the response. 
    Return 'products' if it is Document 1, 'data' if it is Document 2, and 'privacy' if it is Document 3. 

    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content" : mensagem_usuario
            }
        ],
        temperature=0.6,
    )

    context = response.choices[0].message.content.lower()

    return context
    