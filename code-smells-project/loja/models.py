"""SQLite persistence for the store domain. HTTP and business rules live elsewhere."""

from .database import get_db


def _produto(row):
    return dict(row) if row else None


def listar_produtos():
    return [_produto(row) for row in get_db().execute("SELECT * FROM produtos ORDER BY id")]


def produto_por_id(produto_id):
    return _produto(get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone())


def buscar_produtos(termo="", categoria=None, preco_min=None, preco_max=None):
    filtros, parametros = [], []
    if termo:
        filtros.append("(nome LIKE ? OR descricao LIKE ?)")
        like = f"%{termo}%"
        parametros.extend((like, like))
    if categoria:
        filtros.append("categoria = ?")
        parametros.append(categoria)
    if preco_min is not None:
        filtros.append("preco >= ?")
        parametros.append(preco_min)
    if preco_max is not None:
        filtros.append("preco <= ?")
        parametros.append(preco_max)
    where = " WHERE " + " AND ".join(filtros) if filtros else ""
    rows = get_db().execute("SELECT * FROM produtos" + where + " ORDER BY id", parametros)
    return [_produto(row) for row in rows]


def inserir_produto(valores):
    cursor = get_db().execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        valores,
    )
    get_db().commit()
    return cursor.lastrowid


def atualizar_produto(produto_id, valores):
    cursor = get_db().execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (*valores, produto_id),
    )
    get_db().commit()
    return cursor.rowcount > 0


def remover_produto(produto_id):
    cursor = get_db().execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    get_db().commit()
    return cursor.rowcount > 0


def listar_usuarios():
    rows = get_db().execute("SELECT id, nome, email, tipo, criado_em FROM usuarios ORDER BY id")
    return [dict(row) for row in rows]


def usuario_por_id(usuario_id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return dict(row) if row else None


def usuario_por_email(email):
    row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def inserir_usuario(nome, email, senha_hash, tipo="cliente"):
    cursor = get_db().execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    get_db().commit()
    return cursor.lastrowid


def usuario_existe(usuario_id):
    return get_db().execute("SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)).fetchone() is not None


def pedidos(usuario_id=None):
    db = get_db()
    if usuario_id is None:
        rows = db.execute("SELECT * FROM pedidos ORDER BY id")
    else:
        rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id", (usuario_id,))
    resultado = []
    for row in rows:
        pedido = dict(row)
        itens = db.execute(
            "SELECT ip.produto_id, COALESCE(p.nome, 'Desconhecido') AS produto_nome, "
            "ip.quantidade, ip.preco_unitario FROM itens_pedido ip "
            "LEFT JOIN produtos p ON p.id = ip.produto_id WHERE ip.pedido_id = ? ORDER BY ip.id",
            (row["id"],),
        )
        pedido["itens"] = [dict(item) for item in itens]
        resultado.append(pedido)
    return resultado


def pedido_por_id(pedido_id):
    return get_db().execute("SELECT id FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()


def criar_pedido(usuario_id, itens):
    db = get_db()
    try:
        db.execute("BEGIN")
        if not usuario_existe(usuario_id):
            return {"erro": "Usuário não encontrado"}
        total = 0
        linhas = []
        for item in itens:
            produto = db.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}
            total += produto["preco"] * item["quantidade"]
            linhas.append((item["produto_id"], item["quantidade"], produto["preco"]))
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid
        for produto_id, quantidade, preco in linhas:
            stock = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (quantidade, produto_id, quantidade),
            )
            if stock.rowcount == 0:
                raise ValueError("Estoque insuficiente")
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, produto_id, quantidade, preco),
            )
        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def atualizar_status(pedido_id, status):
    cursor = get_db().execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
    get_db().commit()
    return cursor.rowcount > 0


def metricas_vendas():
    db = get_db()
    total_pedidos, = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()
    faturamento, = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()
    contagens = {status: db.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)).fetchone()[0]
                 for status in ("pendente", "aprovado", "cancelado")}
    return total_pedidos, faturamento, contagens


def contagem_tabelas():
    db = get_db()
    return {
        tabela: db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        for tabela in ("produtos", "usuarios", "pedidos")
    }


def resetar_dados():
    db = get_db()
    try:
        db.execute("BEGIN")
        for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            db.execute(f"DELETE FROM {tabela}")
        db.commit()
    except Exception:
        db.rollback()
        raise
