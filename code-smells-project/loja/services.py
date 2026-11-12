"""Use cases and domain validation for the store API."""

import math

from werkzeug.security import check_password_hash, generate_password_hash

from . import models
from .constants import (
    CATEGORIAS_VALIDAS, CATEGORIA_PADRAO, NOME_PRODUTO_TAMANHO_MAXIMO,
    NOME_PRODUTO_TAMANHO_MINIMO, STATUS_PEDIDO_VALIDOS, TIPO_USUARIO_PADRAO,
)
from .errors import DomainError


def _produto_valores(dados):
    if not isinstance(dados, dict):
        raise DomainError("Dados inválidos")
    for campo, rotulo in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
        if campo not in dados:
            raise DomainError(f"{rotulo} é obrigatório")
    nome, descricao = dados["nome"], dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    if not isinstance(nome, str):
        raise DomainError("Nome inválido")
    if len(nome) < NOME_PRODUTO_TAMANHO_MINIMO:
        raise DomainError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_TAMANHO_MAXIMO:
        raise DomainError("Nome muito longo")
    try:
        preco, estoque = float(dados["preco"]), int(dados["estoque"])
    except (TypeError, ValueError, OverflowError):
        raise DomainError("Preço ou estoque inválido") from None
    if not math.isfinite(preco) or preco < 0:
        raise DomainError("Preço não pode ser negativo")
    if estoque < 0 or isinstance(dados["estoque"], bool):
        raise DomainError("Estoque não pode ser negativo")
    if not isinstance(descricao, str) or not isinstance(categoria, str):
        raise DomainError("Descrição ou categoria inválida")
    if categoria not in CATEGORIAS_VALIDAS:
        raise DomainError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))
    return nome, descricao, preco, estoque, categoria


def criar_produto(dados):
    return models.inserir_produto(_produto_valores(dados))


def atualizar_produto(produto_id, dados):
    if not models.produto_por_id(produto_id):
        raise DomainError("Produto não encontrado", 404)
    models.atualizar_produto(produto_id, _produto_valores(dados))


def deletar_produto(produto_id):
    if not models.remover_produto(produto_id):
        raise DomainError("Produto não encontrado", 404)


def _hash_senha(senha):
    return generate_password_hash(senha, method="scrypt")


def criar_usuario(dados):
    if not isinstance(dados, dict):
        raise DomainError("Dados inválidos")
    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not all(isinstance(valor, str) and valor for valor in (nome, email, senha)):
        raise DomainError("Nome, email e senha são obrigatórios")
    try:
        return models.inserir_usuario(nome, email, _hash_senha(senha), TIPO_USUARIO_PADRAO)
    except Exception as error:
        if "unique" in str(error).lower():
            raise DomainError("Email já cadastrado", 409) from None
        raise


def login(dados):
    if not isinstance(dados, dict):
        raise DomainError("Email e senha são obrigatórios")
    email, senha = dados.get("email", ""), dados.get("senha", "")
    if not isinstance(email, str) or not isinstance(senha, str) or not email or not senha:
        raise DomainError("Email e senha são obrigatórios")
    usuario = models.usuario_por_email(email)
    if not usuario or not check_password_hash(usuario["senha"], senha):
        raise DomainError("Email ou senha inválidos", 401, incluir_sucesso=True)
    return {"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"], "tipo": usuario["tipo"]}


def criar_pedido(dados):
    if not isinstance(dados, dict):
        raise DomainError("Dados inválidos")
    usuario_id, itens = dados.get("usuario_id"), dados.get("itens", [])
    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool) or usuario_id <= 0:
        raise DomainError("Usuario ID é obrigatório")
    if not isinstance(itens, list) or not itens:
        raise DomainError("Pedido deve ter pelo menos 1 item")
    normalizados = []
    for item in itens:
        if not isinstance(item, dict):
            raise DomainError("Item inválido")
        produto_id, quantidade = item.get("produto_id"), item.get("quantidade")
        if (not isinstance(produto_id, int) or isinstance(produto_id, bool) or produto_id <= 0
                or not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0):
            raise DomainError("Produto e quantidade inválidos")
        normalizados.append({"produto_id": produto_id, "quantidade": quantidade})
    resultado = models.criar_pedido(usuario_id, normalizados)
    if "erro" in resultado:
        raise DomainError(resultado["erro"])
    return resultado


def atualizar_status(pedido_id, dados):
    if not isinstance(dados, dict):
        raise DomainError("Status inválido")
    status = dados.get("status", "")
    if status not in STATUS_PEDIDO_VALIDOS:
        raise DomainError("Status inválido")
    if not models.atualizar_status(pedido_id, status):
        raise DomainError("Pedido não encontrado", 404)
    return status


def resumo_vendas():
    total_pedidos, faturamento, contagens = models.metricas_vendas()
    desconto = next((faturamento * taxa for limite, taxa in ((10000, .1), (5000, .05), (1000, .02))
                     if faturamento > limite), 0)
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": contagens["pendente"],
        "pedidos_aprovados": contagens["aprovado"],
        "pedidos_cancelados": contagens["cancelado"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
    }
