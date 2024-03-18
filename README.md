# site-teste

Teste de site usando o [Render](https://render.com/).

## Configurando o webhook

Para que o código funcione é preciso configurar o webhook do Telegram, executando (pode ser em um notebook do Colab) o
seguinte código:

```python
import requests
token = "..."  # Altere para o token do seu robô
dados = {"url": "https://seu-site-do-render.onrender.com/telegram"}  # Altere para a URL do seu site
resposta = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data=dados)
print(resposta.json())
```

Além disso, é necessário configurar a variável de ambiente `TELEGRAM_BOT_TOKEN` no Render com o token do seu robô.
