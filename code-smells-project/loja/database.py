"""Ciclo de vida da conexão SQLite, schema e dados de exemplo.

A conexão vive no contexto de aplicação do Flask (`flask.g`) e é fechada no
teardown da requisição. Não existe conexão global mutável.
"""

import logging
import os
import secrets
import sqlite3

from flask import current_app, g

LOGGER = logging.getLogger(__name__)

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
)

PRODUTOS_EXEMPLO = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Os usuários de exemplo são criados com hash derivado por KDF. As senhas de
# demonstração vêm de variável de ambiente (SEED_PASSWORD_<SLUG>) ou são geradas
# aleatoriamente; nenhum valor de credencial é fixado neste arquivo.
USUARIOS_EXEMPLO = [
    ("ADMIN", "Admin", "admin@loja.com", "admin"),
    ("JOAO", "João Silva", "joao@email.com", "cliente"),
    ("MARIA", "Maria Santos", "maria@email.com", "cliente"),
]


def get_db():
    """Conexão da requisição atual, criada sob demanda."""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE_PATH"])
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def close_db(exception=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_schema(connection):
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()


def seed_if_empty(connection, senhas_exemplo=None):
    """Insere dados de exemplo apenas quando a tabela de produtos está vazia."""
    from werkzeug.security import generate_password_hash

    cursor = connection.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] != 0:
        return False

    connection.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        PRODUTOS_EXEMPLO,
    )

    senhas_exemplo = senhas_exemplo or {}
    usuarios = []
    for slug, nome, email, tipo in USUARIOS_EXEMPLO:
        senha = senhas_exemplo.get(email) or os.environ.get(f"SEED_PASSWORD_{slug}")
        if not senha:
            senha = secrets.token_urlsafe(16)
            LOGGER.warning(
                "Senha de exemplo gerada aleatoriamente e não registrada. "
                "Defina SEED_PASSWORD_%s para controlar o valor.",
                slug,
            )
        usuarios.append((nome, email, generate_password_hash(senha, method="scrypt"), tipo))

    connection.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        usuarios,
    )
    connection.commit()
    LOGGER.info("Dados de exemplo inseridos: %d produtos, %d usuários.",
                len(PRODUTOS_EXEMPLO), len(usuarios))
    return True


def migrate_passwords(connection):
    """Upgrade legacy plaintext passwords once, without logging credential data."""
    from werkzeug.security import generate_password_hash

    rows = connection.execute("SELECT id, senha FROM usuarios").fetchall()
    migrated = 0
    for row in rows:
        value = row["senha"] or ""
        if not value.startswith(("scrypt:", "pbkdf2:")):
            connection.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(value, method="scrypt"), row["id"]),
            )
            migrated += 1
    if migrated:
        connection.commit()
        LOGGER.info("Migradas %d senhas legadas para hash seguro.", migrated)


def init_app(app):
    app.teardown_appcontext(close_db)
