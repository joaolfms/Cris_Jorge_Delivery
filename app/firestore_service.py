# app/firestore_service.py

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional, Dict
from datetime import datetime
import pytz

from .models import MenuItem, ConversationState, Order, OrderItem

class FirestoreService:
    """
    Classe para encapsular todas as interações com o Google Cloud Firestore.
    """
    def __init__(self):
        """
        Inicializa a conexão com o Firestore usando as credenciais do ambiente.
        """
        if not firebase_admin._apps:
            # Carrega as credenciais do Firebase a partir da variável de ambiente.
            # O JSON deve estar em uma única linha.
            firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if not firebase_creds_json:
                raise ValueError("A variável de ambiente FIREBASE_CREDENTIALS_JSON não está definida.")

            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        self.timezone = pytz.timezone('America/Sao_Paulo')

    def get_menu(self) -> List[MenuItem]:
        """
        Busca todos os itens do cardápio da coleção 'menu'.
        """
        menu_ref = self.db.collection('menu').stream()
        menu = []
        for item in menu_ref:
            item_data = item.to_dict()
            item_data['id'] = item.id
            menu.append(MenuItem(**item_data))
        return menu

    def get_conversation_state(self, phone_number: str) -> Optional[ConversationState]:
        """
        Recupera o estado da conversa de um usuário pelo número de telefone.
        """
        doc_ref = self.db.collection('conversations').document(phone_number)
        doc = doc_ref.get()
        if doc.exists:
            return ConversationState(**doc.to_dict())
        return None

    def save_conversation_state(self, state: ConversationState):
        """
        Salva ou atualiza o estado da conversa de um usuário.
        """
        state.last_interaction = datetime.now(self.timezone).isoformat()
        doc_ref = self.db.collection('conversations').document(state.phone_number)
        # Usamos `model_dump()` do Pydantic V2 para converter o modelo em um dicionário
        doc_ref.set(state.model_dump())

    def create_order(self, state: ConversationState, address: str) -> Order:
        """
        Cria um novo pedido no Firestore a partir do estado da conversa e do endereço.
        """
        # Converte o dicionário de OrderItem de volta para uma lista
        items_list = list(state.current_order.values())
        
        total_price = sum(item.quantity * item.unit_price for item in items_list)

        new_order = Order(
            customer_phone=state.phone_number,
            items=items_list,
            total_price=total_price,
            status="confirmed",
            address=address,
            created_at=datetime.now(self.timezone).isoformat()
        )

        # Adiciona o pedido à coleção 'orders' e obtém o ID gerado
        update_time, order_ref = self.db.collection('orders').add(new_order.model_dump(exclude={'order_id'}))
        
        # Atualiza o modelo com o ID do documento
        new_order.order_id = order_ref.id
        return new_order

    def clear_conversation_state(self, phone_number: str):
        """
        Limpa o estado da conversa após o pedido ser finalizado,
        retornando ao estado inicial.
        """
        initial_state = ConversationState(
            phone_number=phone_number,
            state="initial",
            current_order={},
            last_interaction=datetime.now(self.timezone).isoformat()
        )
        self.save_conversation_state(initial_state)

# Instância única do serviço para ser usada em toda a aplicação
firestore_service = FirestoreService()
