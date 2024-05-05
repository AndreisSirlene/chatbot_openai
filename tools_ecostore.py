from flask import Flask, render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from select_persona import *
from select_doc import *

load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))
model = "gpt-4"

#Create global variable
my_tools = [
        {
         "type": "function",
         "function": {
            "name": "validate_promotional_code",
            "description": "Validate a promotional code based on Company Discount and Promotion Guidelines",
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "The promotional code in the format, COUPON_XX. For example: COUPON_ECO.",
                    },
                    "validade": {
                        "type": "string",
                        "description": "The validity of the coupon, if valid and associated with the policies. In the format DD/MM/YYYY.",
                    },
                },
                "required": ["codigo", "validade"],
            }
        }
    }
]

def validate_promotional_code(argumentos):
    codigo = argumentos.get("codigo")
    validade = argumentos.get("validade")
    return f"""
        # Answer Format
        {codigo}  with validation date {validade}.
        And, return if ]s valid or not for the user.
        """
        
my_functions = {
    "validate_promotional_code": validate_promotional_code
}
