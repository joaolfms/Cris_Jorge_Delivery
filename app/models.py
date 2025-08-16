# app/models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- Modelos do Cardápio ---

class MenuItem(BaseModel):
    """
    Representa um único item no cardápio.
    """
    id: str = Field(..., description="ID único do item (ex: 'burguer-artesanal')")
    name: str = Field(..., description="Nome do item (ex: 'Burger Artesanal')")
    description: str = Field(..., description="Descrição do item")
    price: float = Field(..., description="Preço do item")
    category: str = Field(..., description="Categoria do item (ex: 'Burgers', 'Bebidas')")

# --- Modelos do Pedido ---

class OrderItem(BaseModel):
    """
    Representa um item dentro de um pedido, incluindo a quantidade.
    """
    item_id: str = Field(..., description="ID do item do cardápio")
    name: str = Field(..., description="Nome do item")
    quantity: int = Field(..., gt=0, description="Quantidade do item")
    unit_price: float = Field(..., description="Preço unitário do item")

class Order(BaseModel):
    """
    Representa um pedido completo de um cliente.
    """
    order_id: Optional[str] = Field(None, description="ID do pedido, gerado pelo Firestore")
    customer_phone: str = Field(..., description="Número de WhatsApp do cliente")
    items: List[OrderItem] = Field(default_factory=list, description="Lista de itens no pedido")
    total_price: float = Field(0.0, description="Preço total do pedido")
    status: str = Field("pending", description="Status do pedido (ex: pending, confirmed, sent_to_kitchen, completed)")
    address: Optional[str] = Field(None, description="Endereço de entrega do cliente")
    created_at: str = Field(..., description="Timestamp de criação do pedido")

# --- Modelo do Estado da Conversa ---

class ConversationState(BaseModel):
    """
    Armazena o estado atual da conversa para um determinado usuário.
    Isso permite que o chatbot saiba em que ponto do fluxo de pedido o usuário está.
    """
    phone_number: str = Field(..., description="Número de WhatsApp do usuário")
    state: str = Field("initial", description="O estado atual da conversa (ex: 'initial', 'ordering', 'confirming_order', 'getting_address')")
    current_order: Dict[str, OrderItem] = Field(default_factory=dict, description="Itens do pedido atual, mapeados por item_id para fácil acesso")
    last_interaction: str = Field(..., description="Timestamp da última interação")

