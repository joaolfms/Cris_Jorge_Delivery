# app/conversation_flow.py

from datetime import datetime
from .firestore_service import firestore_service
from .whatsapp_client import whatsapp_client
from .models import ConversationState, MenuItem, OrderItem
import os

# --- Funções Auxiliares de Formatação ---

def format_menu(menu: list[MenuItem]) -> str:
    """Formata o cardápio em uma string legível."""
    response = "Nosso cardápio de hoje:\n\n"
    categories = {}
    for item in menu:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)

    for category, items in categories.items():
        response += f"*{category}*\n"
        for item in items:
            response += f"  - `{item.id}`: {item.name} - R$ {item.price:.2f}\n"
            response += f"    _{item.description}_\n"
        response += "\n"
    
    response += "Para adicionar um item, digite `adicionar <id_do_item> <quantidade>`.\n"
    response += "Exemplo: `adicionar burguer-artesanal 2`"
    return response

def format_cart(state: ConversationState) -> str:
    """Formata o carrinho de compras em uma string legível."""
    if not state.current_order:
        return "Seu carrinho está vazio."

    response = "🛒 *Seu Carrinho:*\n"
    total = 0.0
    for item_id, order_item in state.current_order.items():
        item_total = order_item.unit_price * order_item.quantity
        response += f"- {order_item.quantity}x {order_item.name}: R$ {item_total:.2f}\n"
        total += item_total
    
    response += f"\n*Total: R$ {total:.2f}*\n\n"
    response += "Digite `confirmar` para finalizar o pedido, `limpar` para esvaziar o carrinho ou continue adicionando itens."
    return response

def format_order_for_kitchen(order) -> str:
    """Formata os detalhes do pedido para notificação na cozinha."""
    message = f"🔔 *Novo Pedido Recebido!* 🔔\n\n"
    message += f"*ID do Pedido:* `{order.order_id}`\n"
    message += f"*Cliente:* {order.customer_phone.replace('whatsapp:', '')}\n"
    message += f"*Endereço:* {order.address}\n\n"
    message += "*Itens:*\n"
    for item in order.items:
        message += f"- {item.quantity}x {item.name}\n"
    message += f"\n*Total do Pedido: R$ {order.total_price:.2f}*"
    return message

# --- Lógica Principal do Chatbot ---

def handle_conversation(phone_number: str, message: str):
    """
    Ponto de entrada para gerenciar a lógica da conversa.
    """
    state = firestore_service.get_conversation_state(phone_number)

    # Se não houver estado, cria um novo (primeira interação do usuário)
    if not state:
        state = ConversationState(
            phone_number=phone_number,
            last_interaction=datetime.now().isoformat()
        )
        firestore_service.save_conversation_state(state)

    # Converte a mensagem para minúsculas para facilitar o processamento
    message = message.lower().strip()

    # Roteamento baseado no estado atual da conversa
    if state.state == "initial":
        handle_initial_state(state, message)
    elif state.state == "ordering":
        handle_ordering_state(state, message)
    elif state.state == "confirming_order":
        handle_confirming_state(state, message)
    elif state.state == "getting_address":
        handle_getting_address_state(state, message)

# --- Manipuladores de Estado (State Handlers) ---

def handle_initial_state(state: ConversationState, message: str):
    """Lida com a primeira interação ou após um pedido ser concluído."""
    response = (
        "Olá! 👋 Bem-vindo(a) ao nosso atendimento automático. "
        "Para ver o cardápio, digite `cardapio`."
    )
    if message == "cardapio":
        menu = firestore_service.get_menu()
        if not menu:
            response = "Desculpe, nosso cardápio não está disponível no momento. Tente novamente mais tarde."
        else:
            response = format_menu(menu)
            state.state = "ordering" # Muda o estado para 'pedindo'
    
    whatsapp_client.send_message(to=state.phone_number, body=response)
    firestore_service.save_conversation_state(state)

def handle_ordering_state(state: ConversationState, message: str):
    """Lida com o usuário enquanto ele está adicionando itens ao carrinho."""
    parts = message.split()
    command = parts[0]
    response = ""

    if command == "adicionar" and len(parts) == 3:
        item_id, quantity_str = parts[1], parts[2]
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError
            
            menu = firestore_service.get_menu()
            menu_item = next((item for item in menu if item.id == item_id), None)

            if menu_item:
                if item_id in state.current_order:
                    # Se o item já está no carrinho, atualiza a quantidade
                    state.current_order[item_id].quantity += quantity
                else:
                    # Adiciona novo item ao carrinho
                    state.current_order[item_id] = OrderItem(
                        item_id=item_id,
                        name=menu_item.name,
                        quantity=quantity,
                        unit_price=menu_item.price
                    )
                response = f"✅ {quantity}x {menu_item.name} adicionado(s) ao seu carrinho!\n\n"
                response += format_cart(state)
            else:
                response = f"❌ Desculpe, o item com ID `{item_id}` não foi encontrado no cardápio."
        except ValueError:
            response = "❌ Comando inválido. Use: `adicionar <id_do_item> <quantidade>`. Ex: `adicionar burguer-artesanal 2`"

    elif command == "carrinho":
        response = format_cart(state)

    elif command == "limpar":
        state.current_order = {}
        response = "Seu carrinho foi esvaziado."

    elif command == "confirmar":
        if not state.current_order:
            response = "Seu carrinho está vazio. Adicione itens antes de confirmar."
        else:
            state.state = "getting_address"
            response = "Por favor, digite seu endereço completo para a entrega."
    
    elif command == "cardapio":
        menu = firestore_service.get_menu()
        response = format_menu(menu)

    else:
        response = "Comando não reconhecido. Use `adicionar`, `carrinho`, `limpar` ou `confirmar`."

    whatsapp_client.send_message(to=state.phone_number, body=response)
    firestore_service.save_conversation_state(state)

def handle_confirming_state(state: ConversationState, message: str):
    """(Não utilizado no fluxo atual, mas pode ser útil para uma etapa de confirmação dupla)"""
    pass # Lógica pode ser adicionada aqui se necessário

def handle_getting_address_state(state: ConversationState, message: str):
    """Lida com a obtenção do endereço do cliente."""
    address = message.strip()
    if len(address) < 10: # Validação simples de endereço
        response = "Por favor, forneça um endereço mais detalhado."
        whatsapp_client.send_message(to=state.phone_number, body=response)
        return

    # Cria o pedido no Firestore
    order = firestore_service.create_order(state, address)

    # Envia confirmação para o cliente
    confirmation_message = (
        f"✅ Pedido confirmado com sucesso!\n\n"
        f"O seu pedido nº `{order.order_id}` já está sendo preparado e logo sairá para entrega no endereço:\n"
        f"_{order.address}_\n\n"
        f"Valor total: *R$ {order.total_price:.2f}*\n\n"
        "Obrigado pela sua preferência!"
    )
    whatsapp_client.send_message(to=state.phone_number, body=confirmation_message)

    # Envia notificação para a cozinha
    kitchen_number = os.getenv("KITCHEN_WHATSAPP_NUMBER")
    if kitchen_number:
        kitchen_message = format_order_for_kitchen(order)
        whatsapp_client.send_message(to=kitchen_number, body=kitchen_message)

    # Limpa o estado da conversa para um novo pedido
    firestore_service.clear_conversation_state(state.phone_number)
