"""Constantes de domínio compartilhadas entre serviços e validadores."""

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]
CATEGORIA_PADRAO = "geral"

NOME_PRODUTO_TAMANHO_MINIMO = 2
NOME_PRODUTO_TAMANHO_MAXIMO = 200

STATUS_PEDIDO_VALIDOS = [
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
]
STATUS_PEDIDO_INICIAL = "pendente"

TIPO_USUARIO_PADRAO = "cliente"

# Faixas de desconto do relatório de vendas: (faturamento mínimo exclusivo, taxa).
# Avaliadas na ordem, da maior faixa para a menor.
FAIXAS_DESCONTO = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)
