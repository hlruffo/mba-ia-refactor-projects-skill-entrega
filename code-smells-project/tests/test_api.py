import sqlite3

import pytest
from werkzeug.security import check_password_hash

from loja import create_app
from loja import models


@pytest.fixture
def app(tmp_path):
    return create_app({
        "DATABASE_PATH": str(tmp_path / "test.sqlite3"),
        "AUTO_INIT_DB": True,
        "SECRET_KEY": "test-only-key",
        "ADMIN_API_ENABLED": False,
        "ADMIN_API_TOKEN": "",
    })


@pytest.fixture
def client(app):
    return app.test_client()


def test_original_public_endpoints_smoke(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json["status"] == "ok"
    assert client.get("/produtos").status_code == 200
    assert client.get("/produtos/busca").status_code == 200
    assert client.get("/produtos/1").status_code == 200
    assert client.get("/usuarios").status_code == 200
    assert client.get("/usuarios/1").status_code == 200
    assert client.get("/pedidos").status_code == 200
    assert client.get("/pedidos/usuario/1").status_code == 200
    assert client.get("/relatorios/vendas").status_code == 200

    user = client.post("/usuarios", json={"nome": "Teste", "email": "test@example.invalid", "senha": "correct horse"})
    assert user.status_code == 201
    login = client.post("/login", json={"email": "test@example.invalid", "senha": "correct horse"})
    assert login.status_code == 200
    user_id = user.json["dados"]["id"]

    product = client.post("/produtos", json={
        "nome": "Produto teste", "preco": 12.5, "estoque": 3, "categoria": "geral",
    })
    assert product.status_code == 201
    product_id = product.json["dados"]["id"]
    assert client.put(f"/produtos/{product_id}", json={
        "nome": "Produto atualizado", "preco": 15, "estoque": 5,
    }).status_code == 200
    order = client.post("/pedidos", json={
        "usuario_id": user_id, "itens": [{"produto_id": product_id, "quantidade": 1}],
    })
    assert order.status_code == 201
    order_id = order.json["dados"]["pedido_id"]
    assert client.put(f"/pedidos/{order_id}/status", json={"status": "aprovado"}).status_code == 200
    assert client.get(f"/pedidos/usuario/{user_id}").json["dados"][0]["status"] == "aprovado"
    assert client.get("/relatorios/vendas").json["dados"]["total_pedidos"] == 1
    assert client.delete(f"/produtos/{product_id}").status_code == 200


def test_users_never_expose_password_hash_and_password_is_hashed(app, client):
    response = client.post("/usuarios", json={
        "nome": "Privacidade", "email": "private@example.invalid", "senha": "not-for-output",
    })
    user_id = response.json["dados"]["id"]
    assert "senha" not in client.get("/usuarios").json["dados"][0]
    assert "senha" not in client.get(f"/usuarios/{user_id}").json["dados"]

    db = sqlite3.connect(app.config["DATABASE_PATH"])
    stored = db.execute("SELECT senha FROM usuarios WHERE id = ?", (user_id,)).fetchone()[0]
    db.close()
    assert stored != "not-for-output"
    assert check_password_hash(stored, "not-for-output")
    assert "not-for-output" not in str(client.post("/login", json={
        "email": "private@example.invalid", "senha": "wrong secret",
    }).json)
    health = client.get("/health").json
    assert not {"secret_key", "db_path", "debug", "admin_api_token"}.intersection(health)


def test_search_is_parameterized_and_login_rejects_sql_injection(client):
    response = client.get("/produtos/busca", query_string={"q": "' OR '1'='1"})
    assert response.status_code == 200
    assert response.json["dados"] == []
    assert client.post("/login", json={
        "email": "' OR 1=1 --", "senha": "anything",
    }).status_code == 401


def test_admin_query_is_disabled_and_reset_is_not_public(client):
    query = client.post("/admin/query", json={"sql": "SELECT * FROM usuarios"})
    assert query.status_code == 410
    assert "dados" not in query.json
    assert client.post("/admin/reset-db").status_code == 404


def test_reset_requires_explicit_enablement_and_bearer_token(tmp_path):
    app = create_app({
        "DATABASE_PATH": str(tmp_path / "admin.sqlite3"), "AUTO_INIT_DB": True,
        "SECRET_KEY": "test-only-key", "ADMIN_API_ENABLED": True,
        "ADMIN_API_TOKEN": "test-admin-token",
    })
    client = app.test_client()
    assert client.post("/admin/reset-db").status_code == 401
    assert client.post("/admin/reset-db", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.post("/admin/reset-db", headers={"Authorization": "Bearer test-admin-token"}).status_code == 200
    assert client.get("/health").json["counts"] == {"produtos": 0, "usuarios": 0, "pedidos": 0}


def test_legacy_plaintext_passwords_are_migrated(tmp_path):
    path = str(tmp_path / "legacy.sqlite3")
    first = create_app({"DATABASE_PATH": path, "AUTO_INIT_DB": True, "SECRET_KEY": "test-only-key"})
    with first.app_context():
        from loja.database import get_db
        get_db().execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            ("Legacy", "legacy@example.invalid", "old-local-password", "cliente"),
        )
        get_db().commit()
    second = create_app({"DATABASE_PATH": path, "AUTO_INIT_DB": True, "SECRET_KEY": "test-only-key"})
    login = second.test_client().post("/login", json={
        "email": "legacy@example.invalid", "senha": "old-local-password",
    })
    assert login.status_code == 200
    db = sqlite3.connect(path)
    stored = db.execute("SELECT senha FROM usuarios WHERE email = ?", ("legacy@example.invalid",)).fetchone()[0]
    db.close()
    assert stored != "old-local-password"


def test_unexpected_errors_are_centralized_and_sanitized(client, monkeypatch, caplog):
    def fail():
        raise RuntimeError("private-error-detail")

    monkeypatch.setattr(models, "listar_produtos", fail)
    response = client.get("/produtos")
    assert response.status_code == 500
    assert response.json == {"erro": "Erro interno do servidor"}
    assert "private-error-detail" not in response.get_data(as_text=True)
    assert "private-error-detail" not in caplog.text
