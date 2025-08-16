# app/main.py

from fastapi import FastAPI, Form, Response, status
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from .conversation_flow import handle_conversation

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="WhatsApp Chatbot API",
    description="Webhook para receber mensagens do WhatsApp via Twilio e processar pedidos.",
    version="1.0.0"
)

@app.post("/webhook")
async def webhook(
    response: Response,
    From: str = Form(...),  # Número do remetente (ex: whatsapp:+55119...)
    Body: str = Form(...)   # Conteúdo da mensagem
):
    """
    Endpoint principal que recebe as requisições POST da Twilio.
    
    A Twilio envia os dados como um formulário (application/x-www-form-urlencoded),
    por isso usamos `Form(...)` para extrair os campos `From` e `Body`.
    """
    print(f"Mensagem recebida de {From}: '{Body}'")

    try:
        # Chama a função principal que gerencia a lógica da conversa
        handle_conversation(phone_number=From, message=Body)
    except Exception as e:
        # Em caso de erro, loga o problema e retorna um status 500
        print(f"ERRO ao processar a mensagem de {From}: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        # É uma boa prática não retornar detalhes do erro para o cliente (Twilio)
        return "Internal Server Error"

    # Retorna uma resposta vazia com status 204 No Content para a Twilio.
    # Isso informa à Twilio que a mensagem foi recebida com sucesso e
    # que nenhuma resposta TwiML é necessária.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/health")
async def health_check():
    """
    Endpoint simples para verificar se a aplicação está no ar.
    Útil para health checks em ambientes de produção.
    """
    return {"status": "ok"}

