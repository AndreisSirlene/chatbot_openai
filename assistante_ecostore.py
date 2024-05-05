from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from select_persona import *
from tools_ecostore import *
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))
model = "gpt-4-1106-preview"

context = carrega("data/ecostore.txt")

def create_id_lists():
    lista_ids_arquivos = []

    file_data = client.files.create(
        file=open("data/ecostore_data.txt", "rb"),
        purpose="assistants"
        )
    lista_ids_arquivos.append(file_data.id)

    file_privacy = client.files.create(
        file=open("data/privacy.txt", "rb"),
        purpose="assistants"
        )
    lista_ids_arquivos.append(file_privacy.id)

    file_products = client.files.create(
        file=open("data/products.txt","rb"),
        purpose="assistants"
        )

    lista_ids_arquivos.append(file_products.id)

    return lista_ids_arquivos


def pegar_json():
    filename = "assistentes.json"
    
    if not os.path.exists(filename):
        thread_id = create_thread()
        file_id_list = create_id_lists()
        assistant_id = create_assistante(file_id_list)
        data = {
            "assistant_id": assistant_id.id,
            "thread_id": thread_id.id,
            "file_ids": file_id_list
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Arquivo 'assistentes.json' criado com sucesso.")
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Arquivo 'assistentes.json' não encontrado.")

def create_thread():
    return client.beta.threads.create()
 
    
def create_assistante(file_ids=[]):
    assistente = client.beta.assistants.create(
        name="Assistant EcoStore",
        instructions = f"""
            You are a customer service chatbot for an e-commerce. 
            You should not answer questions that are not about the given e-commerce data! 
            Additionally, access files associated to you and a thread to answer customer inqueries.
  
        """,
        model = model,
        tools= my_tools
        
    )
    return assistente

