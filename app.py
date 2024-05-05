from flask import Flask, render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from select_persona import *
from select_doc import *
from assistante_ecostore import *
#from vision_ecostore import analisar_imagem
import uuid 

load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))
model = "gpt-4"

app = Flask(__name__)
app.secret_key = 'alura'

assistente = pegar_json()
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

STATUS_COMPLETED = "completed"
STATUS_REQUIRES_ACTION = "requires_action"


def bot(prompt):
    max_attempts = 1
    repeticao = 0
    
    while True:
        try:
            personality = personas[select_persona(prompt)]
          
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role = "user",
                content = f"""
                From now on, assume the personality below. Ignore previous personalities.
            
                # Persona
                {personality}
                """,
                file_ids = file_ids
            )
            
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role = "user",
                content = prompt
               
            )
            
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistente_id
            )
            while run.status != STATUS_COMPLETED:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
            )
                print(f"Status: {run.status}")
                
            if run.status ==  STATUS_REQUIRES_ACTION:
               tools_acionadas = run.required_action.submit_tool_outputs.tool_calls
               respostas_tools_acionadas = []     
               for uma_tool in tools_acionadas:
                    nome_funcao = uma_tool.function.name
                    funcao_escolhida = my_functions[nome_funcao]
                    argumentos = json.loads(uma_tool.function.arguments)
                    print(argumentos)
                    resposta_funcao = funcao_escolhida(argumentos)
                    
                    respostas_tools_acionadas.append({
                        "tool_call_id": uma_tool.id,
                        "output": resposta_funcao
                    })
                
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id = thread_id,
                run_id = run.id,
                tool_outputs=respostas_tools_acionadas
        )
                    
            
            historico = list(client.beta.threads.messages.list(thread_id=thread_id).data)
            response = historico[0]
            return response
        
        except Exception as erro:
                repeticao += 1
                if repeticao >= max_attempts:
                        return "Erro no GPT: %s" % erro
                print('Error of communication with OpenAI:', erro)
                sleep(1)


@app.route("/chat", methods = ["POST"])
def chat():
    prompt = request.json["msg"]
    response = bot(prompt)
    
    if isinstance(response, str):
        # If response is a string, return it directly
        return response
    elif "content" in response and response["content"]:
        # If response has content attribute and content is not empty
        texto_resposta = response["content"][0]["text"]["value"]
        return texto_resposta
    else:
        # Handle cases where response does not have expected structure
        return "Error: Unexpected response format"
    

@app.route("/")
def home():
    return render_template("index.html")

if __name__== "__main__":
    app.run(debug= True)


