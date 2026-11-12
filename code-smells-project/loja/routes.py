"""HTTP routes; response formatting only, with business rules in services."""

import hmac

from flask import Blueprint, current_app, jsonify, request

from . import models, services
from .errors import DomainError

api = Blueprint("api", __name__)


@api.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja", "versao": current_app.config["APP_VERSION"],
        "endpoints": {"produtos": "/produtos", "usuarios": "/usuarios", "pedidos": "/pedidos",
                      "login": "/login", "relatorios": "/relatorios/vendas", "health": "/health"},
    })


@api.get("/produtos")
def listar_produtos():
    return jsonify({"dados": models.listar_produtos(), "sucesso": True})


@api.get("/produtos/busca")
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    try:
        preco_min = float(request.args["preco_min"]) if "preco_min" in request.args else None
        preco_max = float(request.args["preco_max"]) if "preco_max" in request.args else None
    except ValueError:
        raise DomainError("Faixa de preço inválida") from None
    resultados = models.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True})


@api.get("/produtos/<int:id>")
def buscar_produto(id):
    produto = models.produto_por_id(id)
    if not produto:
        raise DomainError("Produto não encontrado", 404)
    return jsonify({"dados": produto, "sucesso": True})


@api.post("/produtos")
def criar_produto():
    produto_id = services.criar_produto(request.get_json(silent=True))
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


@api.put("/produtos/<int:id>")
def atualizar_produto(id):
    services.atualizar_produto(id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"})


@api.delete("/produtos/<int:id>")
def deletar_produto(id):
    services.deletar_produto(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"})


@api.get("/usuarios")
def listar_usuarios():
    return jsonify({"dados": models.listar_usuarios(), "sucesso": True})


@api.get("/usuarios/<int:id>")
def buscar_usuario(id):
    usuario = models.usuario_por_id(id)
    if not usuario:
        raise DomainError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True})


@api.post("/usuarios")
def criar_usuario():
    usuario_id = services.criar_usuario(request.get_json(silent=True))
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@api.post("/login")
def login():
    usuario = services.login(request.get_json(silent=True))
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"})


@api.post("/pedidos")
def criar_pedido():
    resultado = services.criar_pedido(request.get_json(silent=True))
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


@api.get("/pedidos")
def listar_todos_pedidos():
    return jsonify({"dados": models.pedidos(), "sucesso": True})


@api.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": models.pedidos(usuario_id), "sucesso": True})


@api.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    services.atualizar_status(pedido_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"})


@api.get("/relatorios/vendas")
def relatorio_vendas():
    return jsonify({"dados": services.resumo_vendas(), "sucesso": True})


@api.get("/health")
def health_check():
    models.get_db().execute("SELECT 1").fetchone()
    return jsonify({"status": "ok", "database": "connected", "counts": models.contagem_tabelas(),
                    "versao": current_app.config["APP_VERSION"]})


@api.post("/admin/reset-db")
def reset_database():
    if not current_app.config["ADMIN_API_ENABLED"]:
        raise DomainError("Não encontrado", 404)
    expected = current_app.config["ADMIN_API_TOKEN"]
    supplied = request.headers.get("Authorization", "")
    token = supplied[7:] if supplied.startswith("Bearer ") else ""
    if not token or not hmac.compare_digest(token, expected):
        raise DomainError("Não autorizado", 401)
    models.resetar_dados()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True})


@api.post("/admin/query")
def executar_query():
    # Kept as a tombstone so old callers receive a deterministic safe response.
    return jsonify({"erro": "Endpoint desabilitado"}), 410
