import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

def ask_gemini(prompt, context=""):
    # Insira sua chave da API Gemini em config.py
    client = genai.Client(api_key=GEMINI_API_KEY)  # GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"
    model = "gemini-2.0-flash-thinking-exp-01-21"
    # Constrói o conteúdo com contexto e prompt
    full_prompt = context + "\n" + prompt if context else prompt
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=full_prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="text/plain",
    )
    response = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if hasattr(chunk, "text"):
            response += chunk.text
    return response.strip() 