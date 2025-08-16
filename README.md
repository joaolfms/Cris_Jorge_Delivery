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



