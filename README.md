# Cris_Jorge_Delivery
Aplicação para delivery de comida caseira

Chatbot de Pedidos para Restaurante via WhatsApp
Este projeto implementa um sistema de chatbot para automatizar o recebimento de pedidos de um restaurante através do WhatsApp. A solução é construída com Python, FastAPI, Twilio e Firestore, e é totalmente containerizada com Docker para facilitar o desenvolvimento e o deploy.

Arquitetura
API/Webhook: FastAPI

API do WhatsApp: Twilio

Banco de Dados: Google Cloud Firestore

Containerização: Docker & Docker Compose

Hospedagem Alvo: AWS EC2

Funcionalidades
Fluxo de Conversa Automatizado: Desde a saudação inicial até a confirmação do pedido.

Gerenciamento de Cardápio: O cardápio é carregado dinamicamente do Firestore.

Carrinho de Compras: Clientes podem adicionar múltiplos itens, ver o carrinho e confirmar o pedido.

Persistência de Estado: O estado da conversa de cada cliente é salvo no Firestore, permitindo que ele continue o pedido de onde parou.

Escalabilidade: A arquitetura containerizada permite escalar a aplicação facilmente conforme a demanda.

Configuração do Ambiente Local (com Docker)
Siga estes passos para rodar a aplicação na sua máquina local para desenvolvimento e testes.

Pré-requisitos
Docker instalado.

Docker Compose instalado.

Passo a Passo
Clonar o Repositório:

git clone <URL_DO_SEU_REPOSITORIO>
cd whatsapp_chatbot

Criar e Configurar o Arquivo de Ambiente:
Renomeie o arquivo de exemplo .env_example para .env e preencha com suas credenciais.

mv .env_example .env

Edite o arquivo .env com suas chaves:

# Credenciais da Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886 # Número da Twilio

# Configuração do Firebase
# ATENÇÃO: Cole o conteúdo do seu JSON de credenciais do Firebase aqui,
# mas em uma única linha, substituindo quebras de linha por \n.
# Exemplo: {"type": "service_account", "project_id": "...", ...}
FIREBASE_CREDENTIALS_JSON='{"type": "service_account", ...}'

# Número do WhatsApp da Cozinha para receber notificações
KITCHEN_WHATSAPP_NUMBER=whatsapp:+55119XXXXXXXX # Número da cozinha

Construir e Iniciar o Container:
Este comando irá construir a imagem Docker (se ainda não existir) e iniciar o serviço da aplicação.

docker-compose up --build

Para rodar em modo detached (em segundo plano), use:

docker-compose up --build -d

A aplicação estará rodando e acessível na porta 8000 da sua máquina local.

Expor o Webhook com ngrok:
Para que a Twilio possa enviar mensagens para a sua aplicação local, você precisa expor sua porta local para a internet. O ngrok é uma ótima ferramenta para isso.

ngrok http 8000

O ngrok irá gerar uma URL pública (ex: https://abcdef123456.ngrok.io).

Configurar o Webhook na Twilio:

Vá para o seu console da Twilio.

Navegue até a seção do seu número de WhatsApp.

Em "Messaging", configure o campo "A MESSAGE COMES IN" com a URL gerada pelo ngrok, adicionando o endpoint /webhook.

Exemplo: https://abcdef123456.ngrok.io/webhook

Salve a configuração. Agora você pode enviar uma mensagem para o seu número da Twilio e interagir com o chatbot.

Deploy em um Servidor AWS EC2
Siga estes passos para implantar a aplicação em um ambiente de produção na AWS.

Pré-requisitos na AWS
Uma conta AWS ativa.

Um par de chaves EC2 (.pem) para acesso SSH à sua instância.

Passo a Passo do Deploy
Provisionar Instância EC2:

Acesse o console da AWS e vá para o serviço EC2.

Clique em "Launch instances".

Escolha uma AMI (Amazon Machine Image), como Ubuntu Server 22.04 LTS.

Escolha um tipo de instância (ex: t2.micro ou t3.small são suficientes para começar).

Selecione seu par de chaves ou crie um novo para poder acessar a instância via SSH.

Configurar o Security Group:
Durante a criação da instância, configure o Security Group para permitir o tráfego nas seguintes portas:

SSH (porta 22): Acesso para você gerenciar o servidor. Restrinja o acesso ao seu IP por segurança.

HTTP (porta 80): Acesso público para o tráfego web.

HTTPS (porta 443): Acesso público para tráfego seguro (essencial para produção).

Instalar Docker e Docker Compose no Servidor:

Conecte-se à sua instância EC2 via SSH:

ssh -i /caminho/para/sua-chave.pem ubuntu@SEU_IP_PUBLICO

Atualize os pacotes e instale o Docker:

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

Importante: Após o último comando, saia da sessão SSH e conecte-se novamente para que a permissão de grupo do Docker seja aplicada.

Instale o Docker Compose:

sudo apt-get install -y docker-compose

Transferir o Projeto para o Servidor:
A forma mais simples é clonar seu repositório Git diretamente no servidor.

git clone <URL_DO_SEU_REPOSITORIO>
cd whatsapp_chatbot

Configurar Variáveis de Ambiente no Servidor:
Crie o arquivo .env no servidor de forma segura. Nunca comite este arquivo no Git.

nano .env

Copie e cole o conteúdo do seu .env local (com as credenciais de produção) neste novo arquivo. Salve e feche (CTRL+X, Y, Enter).

Iniciar a Aplicação:
Use o Docker Compose para iniciar a aplicação em modo detached.

docker-compose up --build -d

Sua aplicação agora está rodando no servidor EC2.

Configurar o Webhook da Twilio (Produção):

Volte ao console da Twilio.

Atualize a URL do webhook para usar o endereço de IP público (ou domínio, se configurado) da sua instância EC2.

Exemplo: http://SEU_IP_PUBLICO/webhook

Salve a configuração. O chatbot está agora ativo em produção.

Boas Práticas para Produção
Configurar um Domínio: Associe um nome de domínio (ex: pedidos.seurestaurante.com) ao IP público da sua instância EC2 usando um registro A no seu provedor de DNS.

Usar um Reverse Proxy com SSL (HTTPS): É altamente recomendável não expor o Uvicorn diretamente à internet. Configure um reverse proxy como Nginx ou Caddy no servidor para:

Gerenciar o tráfego nas portas 80 e 443.

Encaminhar as requisições para a porta da sua aplicação (porta 8000).

Lidar com a terminação SSL/TLS (HTTPS), garantindo que a comunicação seja criptografada. Ferramentas como o Certbot podem ser usadas para obter certificados SSL gratuitos do Let's Encrypt.
