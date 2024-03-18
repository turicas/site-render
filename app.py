import os
import re
import unicodedata

import requests
from flask import Flask, request
from lxml.html import document_fromstring


TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

def normaliza(texto):
  "Normaliza um texto retirando acentos, caracteres especiais e espaços desnecessários"
  texto = texto.lower()
  texto = unicodedata.normalize("NFKD", texto).encode("ascii", errors="ignore").decode("ascii")
  texto = re.sub(r"[^\w\s]", "", texto)
  texto = re.sub(r"\s+", " ", texto)
  return texto.strip()


def materias_home_estadao():
  "Retorna matérias encontradas na home do Estadão"
  response = requests.get("https://www.estadao.com/")
  tree = document_fromstring(response.content)
  tree.xpath("//a[contains(//h2/@class, 'headline')]")
  materias = tree.xpath("//a[contains(./h2/@class, 'headline')]")
  resultado = []
  for materia in materias:
    texto = materia.xpath("./h2//text()")
    if not texto:
      continue
    titulo = " ".join(texto).strip()
    link = materia.xpath("./@href")[0]
    resultado.append({"titulo": titulo, "url": link})
  return resultado


app = Flask(__name__)

@app.route("/")
def index():
  return "Olá, <b>tudo bem</b>?"


@app.route("/estadao")
def estadao():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ronda Estadão</title>
    </head>
    <body>
        <h1>Ronda Estadão</h1>
        <p>
        As matérias encontradas foram:
        <ul>
    """
    for materia in materias_home_estadao():
        palavras = normaliza(materia["titulo"]).split(" ")
        if "dengue" in palavras or "lula" in palavras or "bolsonaro" in palavras:
            html += f'<li> <a href="{materia["url"]}">{materia["titulo"]}</a> </li>'
    html += """
        </ul>
        </p>
    </body>
    </html>
    """
    return html


@app.route("/telegram", methods=["POST"])
def telegram_update():
    # Primeiro, vamos preparar os dados que recebemos
    update = request.json  # Maneira de pegar o conteúdo enviado pelo Telegram
    url_envio_mensagem = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    first_name = update["message"]["from"]["first_name"]
    text = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]
    normalizado = normaliza(text)
    palavras = normalizado.split(" ")

    # Agora, vamos interpretar o que foi enviado para responder
    if text == "/start":
        resposta = "Bem-vindo(a)"
    elif "oi" in palavras or "ola" in palavras:  # Essa verificação irá dar match com "boi"
        resposta = "Olá, como vai?"
    else:
        resposta = "Não entendi!"
    mensagem = {"chat_id": chat_id, "text": resposta}
    resultado = requests.post(url_envio_mensagem, data=mensagem)
    # TODO: fazer algo se `not resultado.ok`

    # Aqui devemos retornar algo para o Telegram, sinalizando que conseguimos receber o webhook sem problemas
    return "ok"
