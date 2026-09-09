from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"

DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT,
            localizacao TEXT,
            status TEXT,
            ultima_leitura TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def listar():
    conn = get_db()
    itens = conn.execute("SELECT * FROM equipamentos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", itens=itens)


@app.route("/novo", methods=["GET", "POST"])
def criar():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()
        localizacao = request.form.get("localizacao", "").strip()
        status = request.form.get("status", "").strip()
        ultima_leitura = request.form.get("ultima_leitura", "").strip()

        if not nome:
            flash("O campo 'Nome' é obrigatório.", "erro")
            return render_template("form.html", item=request.form, acao="Novo")

        conn = get_db()
        conn.execute(
            "INSERT INTO equipamentos (nome, tipo, localizacao, status, ultima_leitura) VALUES (?, ?, ?, ?, ?)",
            (nome, tipo, localizacao, status, ultima_leitura),
        )
        conn.commit()
        conn.close()
        flash("Registro criado com sucesso!", "sucesso")
        return redirect(url_for("listar"))

    return render_template("form.html", item=None, acao="Novo")


@app.route("/editar/<int:item_id>", methods=["GET", "POST"])
def editar(item_id):
    conn = get_db()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()
        localizacao = request.form.get("localizacao", "").strip()
        status = request.form.get("status", "").strip()
        ultima_leitura = request.form.get("ultima_leitura", "").strip()

        if not nome:
            flash("O campo 'Nome' é obrigatório.", "erro")
            conn.close()
            return render_template("form.html", item=request.form, acao="Editar", item_id=item_id)

        conn.execute(
            "UPDATE equipamentos SET nome=?, tipo=?, localizacao=?, status=?, ultima_leitura=? WHERE id=?",
            (nome, tipo, localizacao, status, ultima_leitura, item_id),
        )
        conn.commit()
        conn.close()
        flash("Registro atualizado com sucesso!", "sucesso")
        return redirect(url_for("listar"))

    item = conn.execute("SELECT * FROM equipamentos WHERE id=?", (item_id,)).fetchone()
    conn.close()

    if item is None:
        flash("Registro não encontrado.", "erro")
        return redirect(url_for("listar"))

    return render_template("form.html", item=item, acao="Editar", item_id=item_id)


@app.route("/apagar/<int:item_id>", methods=["POST"])
def apagar(item_id):
    conn = get_db()
    conn.execute("DELETE FROM equipamentos WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    flash("Registro apagado.", "sucesso")
    return redirect(url_for("listar"))


# Garante que a tabela existe também quando rodando via gunicorn (produção)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
