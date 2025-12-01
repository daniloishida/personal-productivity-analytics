# app/web.py
from flask import Flask, request, redirect, jsonify
from datetime import datetime

from .models import init_db, SessionLocal, Task, Expense

app = Flask(__name__)
init_db()

# -------------------------
# CATEGORIAS PADRONIZADAS
# -------------------------
TASK_CATEGORIES = [
    "pessoal",
    "profissional",
    "saude",
    "estudos",
    "familia",
    "financeiro",
]

EXPENSE_CATEGORIES = [
    "alimentacao",
    "transporte",
    "assinaturas",
    "mercado",
    "lazer",
    "saude",
    "outros",
]


def html_page(title: str, body: str) -> str:
    # Atenção: {{ e }} por causa do f-string
    return f"""
    <!doctype html>
    <html lang="pt-br">
      <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; }}
          h1 {{ margin-bottom: 1rem; }}
          nav a {{ margin-right: 1rem; }}
          form {{ margin-top: 1rem; margin-bottom: 2rem; }}
          label {{ display: block; margin-top: 0.5rem; }}
          input, select {{ padding: 0.3rem; width: 300px; }}
          table {{ border-collapse: collapse; margin-top: 1rem; }}
          th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.7rem; }}
        </style>
      </head>
      <body>
        <h1>Personal Productivity Analytics</h1>
        <nav>
          <a href="/">Início</a>
          <a href="/task/new">Nova Task</a>
          <a href="/expense/new">Nova Despesa</a>
          <a href="/expenses">Ver Despesas</a>
        </nav>
        <hr>
        {body}
      </body>
    </html>
    """


@app.route("/")
def index():
    body = """
    <p>Bem-vindo! Aqui você pode cadastrar tasks e despesas diretamente no banco.</p>
    <ul>
      <li>Use os links acima para adicionar dados.</li>
      <li>A API está disponível em <code>/api/tasks</code> e <code>/api/expenses</code>.</li>
    </ul>
    """
    return html_page("Início", body)


# ======================================
# FORMULÁRIO DE TASK
# ======================================
@app.route("/task/new", methods=["GET", "POST"])
def add_task_form():
    if request.method == "POST":
        title = request.form.get("title") or "Tarefa sem título"
        category = request.form.get("category") or "pessoal"
        completed_raw = request.form.get("completed_at", "").strip()
        duration_raw = request.form.get("duration_minutes", "30").strip()

        # Garante categoria válida
        if category not in TASK_CATEGORIES:
            category = "pessoal"

        # Data/hora
        if completed_raw:
            try:
                completed_at = datetime.strptime(completed_raw, "%Y-%m-%d %H:%M")
            except ValueError:
                completed_at = datetime.now()
        else:
            completed_at = datetime.now()

        # Duração
        try:
            duration = int(duration_raw)
        except ValueError:
            duration = 30

        session = SessionLocal()
        try:
            task = Task(
                external_id=None,
                title=title,
                category=category,
                completed_at=completed_at,
                duration_minutes=duration,
            )
            session.add(task)
            session.commit()
        finally:
            session.close()

        return redirect("/")

    # GET: mostra formulário
    cat_options = "".join(
        f'<option value="{c}">{c}</option>' for c in TASK_CATEGORIES
    )

    body = f"""
    <h2>Nova Task</h2>
    <p><strong>Categorias aceitas:</strong> {", ".join(TASK_CATEGORIES)}</p>
    <form method="post">
      <label>Título:
        <input type="text" name="title" required>
      </label>
      <label>Categoria:
        <select name="category">
          {cat_options}
        </select>
      </label>
      <label>Data/hora conclusão (YYYY-MM-DD HH:MM) [opcional]:
        <input type="text" name="completed_at">
      </label>
      <label>Duração (minutos):
        <input type="number" name="duration_minutes" value="30">
      </label>
      <button type="submit">Salvar</button>
    </form>
    """
    return html_page("Nova Task", body)


# ======================================
# FORMULÁRIO DE DESPESA
# ======================================
@app.route("/expense/new", methods=["GET", "POST"])
def add_expense_form():
    if request.method == "POST":
        date_raw = request.form.get("date", "").strip()
        category = request.form.get("category") or "alimentacao"
        description = request.form.get("description") or ""
        amount_raw = request.form.get("amount", "0").strip()

        # Garante categoria válida
        if category not in EXPENSE_CATEGORIES:
            category = "outros"

        # Data
        if date_raw:
            try:
                date_val = datetime.strptime(date_raw, "%Y-%m-%d")
            except ValueError:
                date_val = datetime.now()
        else:
            date_val = datetime.now()

        # Valor
        try:
            amount = float(amount_raw.replace(",", "."))
        except ValueError:
            amount = 0.0

        session = SessionLocal()
        try:
            expense = Expense(
                date=date_val,
                category=category,
                description=description,
                amount=amount,
            )
            session.add(expense)
            session.commit()
        finally:
            session.close()

        return redirect("/expenses")

    # GET: mostra formulário
    cat_options = "".join(
        f'<option value="{c}">{c}</option>' for c in EXPENSE_CATEGORIES
    )

    body = f"""
    <h2>Nova Despesa</h2>
    <p><strong>Categorias aceitas:</strong> {", ".join(EXPENSE_CATEGORIES)}</p>
    <form method="post">
      <label>Data (YYYY-MM-DD) [opcional]:
        <input type="text" name="date">
      </label>
      <label>Categoria:
        <select name="category">
          {cat_options}
        </select>
      </label>
      <label>Descrição:
        <input type="text" name="description">
      </label>
      <label>Valor (R$):
        <input type="number" step="0.01" name="amount" value="0.00">
      </label>
      <button type="submit">Salvar</button>
    </form>
    """
    return html_page("Nova Despesa", body)


# ======================================
# LISTAGEM DE DESPESAS
# ======================================
@app.route("/expenses")
def list_expenses():
    session = SessionLocal()
    try:
        expenses = session.query(Expense).order_by(Expense.date.desc()).limit(50).all()
    finally:
        session.close()

    rows = ""
    for e in expenses:
        date_txt = e.date.strftime("%Y-%m-%d") if e.date else ""
        rows += f"""
        <tr>
          <td>{date_txt}</td>
          <td>{e.category}</td>
          <td>{e.description}</td>
          <td>{e.amount:.2f}</td>
        </tr>
        """

    body = f"""
    <h2>Últimas despesas</h2>
    <table>
      <tr>
        <th>Data</th><th>Categoria</th><th>Descrição</th><th>Valor (R$)</th>
      </tr>
      {rows}
    </table>
    """
    return html_page("Despesas", body)


# ======================================
# API JSON – TASKS
# ======================================
@app.route("/api/tasks")
def api_tasks():
    session = SessionLocal()
    try:
        tasks = session.query(Task).order_by(Task.completed_at.desc()).limit(100).all()
        data = [
            {
                "id": t.id,
                "title": t.title,
                "category": t.category,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "duration_minutes": t.duration_minutes,
            }
            for t in tasks
        ]
    finally:
        session.close()

    return jsonify(data)


# ======================================
# API JSON – EXPENSES
# ======================================
@app.route("/api/expenses")
def api_expenses():
    session = SessionLocal()
    try:
        expenses = session.query(Expense).order_by(Expense.date.desc()).limit(100).all()
        data = [
            {
                "id": e.id,
                "date": e.date.isoformat() if e.date else None,
                "category": e.category,
                "description": e.description,
                "amount": float(e.amount),
            }
            for e in expenses
        ]
    finally:
        session.close()

    return jsonify(data)
