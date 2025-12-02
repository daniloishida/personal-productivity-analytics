# app/web.py
"""
Aplicação Flask do Personal Productivity Analytics.

Rotas HTML:
- /              -> visão geral com métricas (tasks + finanças)
- /tasks         -> listagem de tasks
- /task/new      -> formulário para criar task
- /expenses      -> listagem de despesas
- /expense/new   -> formulário para criar despesa

Rotas API:
- /api/tasks     -> JSON com tasks
- /api/expenses  -> JSON com despesas
"""

from datetime import datetime

from flask import Flask, jsonify, request, redirect, url_for
from sqlalchemy import func, desc

from .database import SessionLocal
from .models import Task, Expense

app = Flask(__name__)

# Categorias padrão (para forms e validação simples)
TASK_CATEGORIES_PT = [
    "pessoal",
    "profissional",
    "saude",
    "estudos",
    "familia",
    "financeiro",
]

EXPENSE_CATEGORIES_PT = [
    "alimentacao",
    "transporte",
    "assinaturas",
    "mercado",
    "lazer",
    "saude",
    "outros",
]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_session():
    return SessionLocal()


def _html_head(title: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px 40px;
      background-color: #f5f5f7;
      color: #222;
    }}
    h1, h2, h3 {{
      font-family: Arial, sans-serif;
    }}
    a {{
      color: #005bbb;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .metric {{
      display: inline-block;
      margin-right: 30px;
      margin-bottom: 15px;
      padding: 10px 14px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    .metric span.label {{
      display: block;
      font-size: 11px;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .metric span.value {{
      font-size: 18px;
      font-weight: bold;
      margin-top: 4px;
    }}
    table {{
      border-collapse: collapse;
      margin-top: 10px;
      width: 100%;
      background: #fff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    th, td {{
      border-bottom: 1px solid #eee;
      padding: 8px 10px;
      font-size: 14px;
    }}
    th {{
      background-color: #f0f2f5;
      text-align: left;
      font-weight: 600;
    }}
    tr:nth-child(even) td {{
      background-color: #fafafa;
    }}
    .btn {{
      display: inline-block;
      padding: 8px 14px;
      margin: 4px 0;
      border-radius: 6px;
      border: none;
      background: #005bbb;
      color: #fff;
      font-size: 14px;
      cursor: pointer;
    }}
    .btn.secondary {{
      background: #555;
    }}
    .btn:hover {{
      opacity: 0.9;
    }}
    .top-links {{
      margin-top: 10px;
      margin-bottom: 20px;
    }}
    .top-links a {{
      margin-right: 15px;
      font-size: 14px;
    }}
    form {{
      background: #fff;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      max-width: 500px;
    }}
    label {{
      display: block;
      margin-top: 10px;
      font-size: 13px;
      font-weight: 600;
    }}
    input[type="text"],
    input[type="number"],
    input[type="datetime-local"],
    input[type="date"],
    select {{
      width: 100%;
      padding: 6px 8px;
      margin-top: 4px;
      border-radius: 4px;
      border: 1px solid #ccc;
      font-size: 14px;
    }}
    .page-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}
  </style>
</head>
<body>
"""


def _html_footer() -> str:
    return """
</body>
</html>
"""


# ---------------------------------------------------------------------
# Rotas HTML
# ---------------------------------------------------------------------

@app.route("/")
def index():
    """
    Home com visão geral dos dados:
    - total de tasks
    - horas totais
    - tasks por categoria
    - total de despesas
    - despesas por categoria
    """
    session = get_session()

    # --- Métricas de tasks ---
    total_tasks = session.query(func.count(Task.id)).scalar() or 0
    total_minutes = session.query(func.sum(Task.duration_minutes)).scalar() or 0.0
    total_hours = round((total_minutes or 0) / 60, 2)

    tasks_by_cat = (
        session.query(
            Task.category,
            func.count(Task.id).label("qtde"),
            func.sum(Task.duration_minutes).label("minutes"),
        )
        .group_by(Task.category)
        .order_by(desc("qtde"))
        .all()
    )

    # --- Métricas de despesas ---
    total_expenses = session.query(func.count(Expense.id)).scalar() or 0
    total_spent = session.query(func.sum(Expense.amount)).scalar() or 0.0

    expenses_by_cat = (
        session.query(
            Expense.category,
            func.count(Expense.id).label("qtde"),
            func.sum(Expense.amount).label("amount"),
        )
        .group_by(Expense.category)
        .order_by(desc("amount"))
        .all()
    )

    session.close()

    html = [
        _html_head("Personal Productivity Analytics"),
        "<h1>📊 Personal Productivity Analytics</h1>",
        "<p>Visão geral das métricas de produtividade e finanças.</p>",
        "<div class='top-links'>",
        "<a href='/tasks'>📋 Ver tasks</a>",
        "<a href='/task/new'>➕ Nova task</a>",
        "<a href='/expenses'>💸 Ver despesas</a>",
        "<a href='/expense/new'>➕ Nova despesa</a>",
        "</div>",
        "<hr/>",
        "<h2>⚙️ Métricas de Agilidade (Tasks)</h2>",
        "<div class='metric'><span class='label'>Tasks concluídas (histórico)</span>",
        f"<span class='value'>{total_tasks}</span></div>",
        "<div class='metric'><span class='label'>Horas totais focadas</span>",
        f"<span class='value'>{total_hours} h</span></div>",
        "<div class='metric'><span class='label'>Tempo total em minutos</span>",
        f"<span class='value'>{int(total_minutes)} min</span></div>",
        "<br/><br/>",
        "<h3>Distribuição por categoria (Tasks)</h3>",
        "<table><tr><th>Categoria</th><th>Qtde Tasks</th><th>Horas</th></tr>",
    ]

    for cat, qtde, mins in tasks_by_cat:
        hours = round((mins or 0) / 60, 2)
        html.append(
            f"<tr><td>{cat}</td><td>{qtde}</td><td>{hours} h</td></tr>"
        )

    # Finanças
    total_spent_fmt = f"R$ {total_spent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    html.extend(
        [
            "</table>",
            "<hr/>",
            "<h2>💰 Métricas Financeiras</h2>",
            "<div class='metric'><span class='label'>Qtde de despesas</span>",
            f"<span class='value'>{total_expenses}</span></div>",
            "<div class='metric'><span class='label'>Gasto total (histórico)</span>",
            f"<span class='value'>{total_spent_fmt}</span></div>",
            "<br/><br/>",
            "<h3>Distribuição por categoria (Despesas)</h3>",
            "<table><tr><th>Categoria</th><th>Qtde</th><th>Total</th></tr>",
        ]
    )

    for cat, qtde, amount in expenses_by_cat:
        amount_fmt = f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        html.append(
            f"<tr><td>{cat}</td><td>{qtde}</td><td>{amount_fmt}</td></tr>"
        )

    html.extend(
        [
            "</table>",
            "<hr/>",
            "<p>",
            "🔗 <a href='/tasks'>Ver últimas tasks</a> | ",
            "<a href='/expenses'>Ver últimas despesas</a> | ",
            "<a href='/api/tasks'>API /tasks</a> | ",
            "<a href='/api/expenses'>API /expenses</a>",
            "</p>",
            _html_footer(),
        ]
    )

    return "\n".join(html)


@app.route("/tasks")
def list_tasks():
    """
    Lista simples das últimas N tasks.
    """
    session = get_session()
    tasks = (
        session.query(Task)
        .order_by(Task.completed_at.desc().nullslast())
        .limit(100)
        .all()
    )
    session.close()

    rows = []
    for t in tasks:
        completed_str = t.completed_at.strftime("%Y-%m-%d %H:%M:%S") if t.completed_at else "-"
        rows.append(
            f"<tr><td>{t.id}</td><td>{t.title}</td><td>{t.category}</td>"
            f"<td>{completed_str}</td><td>{t.duration_minutes}</td></tr>"
        )

    html = [
        _html_head("Tasks"),
        "<div class='page-header'>",
        "<h1>📋 Tasks</h1>",
        "<div>",
        "<a href='/' class='btn secondary'>⬅ Voltar</a> ",
        "<a href='/task/new' class='btn'>➕ Nova task</a>",
        "</div>",
        "</div>",
        "<table><tr><th>ID</th><th>Título</th><th>Categoria</th><th>Concluída em</th><th>Duração (min)</th></tr>",
        *rows,
        "</table>",
        _html_footer(),
    ]

    return "\n".join(html)


@app.route("/task/new", methods=["GET", "POST"])
def create_task():
    """
    Formulário para criar uma nova task.
    Salva direto no banco.
    """
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        category = (request.form.get("category") or "").strip().lower()
        duration_str = request.form.get("duration_minutes") or "0"
        completed_str = request.form.get("completed_at") or ""

        if not title:
            return "Título é obrigatório", 400

        try:
            duration = float(duration_str)
        except ValueError:
            duration = 0.0

        completed_at = None
        if completed_str:
            try:
                # datetime-local vem como "YYYY-MM-DDTHH:MM"
                completed_at = datetime.strptime(completed_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                completed_at = None

        if completed_at is None:
            return "Data de conclusão é obrigatória e deve ser válida", 400

        # external_id único via timestamp em ms
        external_id = str(int(datetime.now().timestamp() * 1000))

        session = get_session()
        task = Task(
            external_id=external_id,
            title=title,
            category=category or "pessoal",
            completed_at=completed_at,
            duration_minutes=duration,
        )
        session.add(task)
        session.commit()
        session.close()

        return redirect(url_for("list_tasks"))

    # GET -> exibe formulário
    options_html = "".join(
        f"<option value='{c}'>{c}</option>" for c in TASK_CATEGORIES_PT
    )

    html = [
        _html_head("Nova Task"),
        "<div class='page-header'>",
        "<h1>➕ Nova Task</h1>",
        "<div><a href='/' class='btn secondary'>⬅ Voltar</a></div>",
        "</div>",
        "<form method='post'>",
        "<label for='title'>Título da task</label>",
        "<input type='text' id='title' name='title' required />",
        "<label for='category'>Categoria</label>",
        f"<select id='category' name='category'>{options_html}</select>",
        "<label for='duration_minutes'>Duração (minutos)</label>",
        "<input type='number' id='duration_minutes' name='duration_minutes' min='0' step='1' value='30' />",
        "<label for='completed_at'>Concluída em</label>",
        "<input type='datetime-local' id='completed_at' name='completed_at' required />",
        "<br/><br/>",
        "<button type='submit' class='btn'>Salvar task</button>",
        "</form>",
        _html_footer(),
    ]

    return "\n".join(html)


@app.route("/expenses")
def list_expenses():
    """
    Lista simples das últimas N despesas.
    """
    session = get_session()
    expenses = (
        session.query(Expense)
        .order_by(Expense.date.desc().nullslast())
        .limit(100)
        .all()
    )
    session.close()

    rows = []
    for e in expenses:
        date_str = e.date.strftime("%Y-%m-%d") if e.date else "-"
        amount_fmt = f"R$ {e.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        rows.append(
            f"<tr><td>{e.id}</td><td>{date_str}</td><td>{e.category}</td>"
            f"<td>{e.description}</td><td>{amount_fmt}</td></tr>"
        )

    html = [
        _html_head("Despesas"),
        "<div class='page-header'>",
        "<h1>💸 Despesas</h1>",
        "<div>",
        "<a href='/' class='btn secondary'>⬅ Voltar</a> ",
        "<a href='/expense/new' class='btn'>➕ Nova despesa</a>",
        "</div>",
        "</div>",
        "<table><tr><th>ID</th><th>Data</th><th>Categoria</th><th>Descrição</th><th>Valor</th></tr>",
        *rows,
        "</table>",
        _html_footer(),
    ]

    return "\n".join(html)


@app.route("/expense/new", methods=["GET", "POST"])
def create_expense():
    """
    Formulário para criar uma nova despesa.
    Salva direto no banco.
    """
    if request.method == "POST":
        category = (request.form.get("category") or "").strip().lower()
        description = (request.form.get("description") or "").strip()
        amount_str = request.form.get("amount") or "0"
        date_str = request.form.get("date") or ""

        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0

        date = None
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date = None

        session = get_session()
        expense = Expense(
            date=date or datetime.now(),
            category=category or "outros",
            description=description,
            amount=amount,
        )
        session.add(expense)
        session.commit()
        session.close()

        return redirect(url_for("list_expenses"))

    options_html = "".join(
        f"<option value='{c}'>{c}</option>" for c in EXPENSE_CATEGORIES_PT
    )

    html = [
        _html_head("Nova Despesa"),
        "<div class='page-header'>",
        "<h1>➕ Nova Despesa</h1>",
        "<div><a href='/' class='btn secondary'>⬅ Voltar</a></div>",
        "</div>",
        "<form method='post'>",
        "<label for='date'>Data</label>",
        "<input type='date' id='date' name='date' />",
        "<label for='category'>Categoria</label>",
        f"<select id='category' name='category'>{options_html}</select>",
        "<label for='description'>Descrição</label>",
        "<input type='text' id='description' name='description' />",
        "<label for='amount'>Valor</label>",
        "<input type='number' id='amount' name='amount' min='0' step='0.01' value='0' />",
        "<br/><br/>",
        "<button type='submit' class='btn'>Salvar despesa</button>",
        "</form>",
        _html_footer(),
    ]

    return "\n".join(html)


# ---------------------------------------------------------------------
# Rotas API (JSON)
# ---------------------------------------------------------------------

@app.route("/api/tasks")
def api_tasks():
    session = get_session()
    tasks = session.query(Task).order_by(Task.completed_at.desc().nullslast()).limit(100).all()
    session.close()

    data = [
        {
            "id": t.id,
            "external_id": t.external_id,
            "title": t.title,
            "category": t.category,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "duration_minutes": t.duration_minutes,
        }
        for t in tasks
    ]
    return jsonify(data)


@app.route("/api/expenses")
def api_expenses():
    session = get_session()
    expenses = session.query(Expense).order_by(Expense.date.desc().nullslast()).limit(100).all()
    session.close()

    data = [
        {
            "id": e.id,
            "date": e.date.isoformat() if e.date else None,
            "category": e.category,
            "description": e.description,
            "amount": e.amount,
        }
        for e in expenses
    ]
    return jsonify(data)
