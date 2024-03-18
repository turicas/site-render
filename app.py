import re
import unicodedata

import requests
from flask import Flask
from lxml.html import document_fromstring


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
