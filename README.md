
# 📊 Personal Productivity Analytics  
Sistema completo de **produtividade + finanças pessoais**, com **ETL, banco SQLite, API Flask, dashboards Streamlit e CLI**.

---

## 🧠 Visão Geral do Projeto  
Este projeto foi criado para ser **realmente útil** no dia a dia — não apenas um portfólio técnico.  
Ele integra:

- ✔ ETL completo (tasks + despesas)
- ✔ Banco SQLite estruturado
- ✔ API e Interface Web (Flask)
- ✔ Dashboard visual (Streamlit)
- ✔ Machine Learning para previsão de gastos
- ✔ Linha de comando (CLI) poderosa
- ✔ Suporte a automações posteriores (Airflow / Cron)

---

# 🏗 Arquitetura Geral

```
personal-productivity-analytics/
│
├── app/
│   ├── etl.py               # Carrega CSVs → banco SQLite (raw → staging → curated)
│   ├── models.py            # ORM: Task, Expense, TimeLog + SessionLocal
│   ├── analytics.py         # Métricas, agregações e KPIs
│   ├── ml.py                # Modelo de previsão (Linear Regression)
│   ├── report.py            # Relatórios e formatação CLI
│   ├── main.py              # CLI do sistema
│   ├── web.py               # Interface Web Flask + API JSON
│   ├── config.py            # Configurações, paths, database
│   └── utils.py             # Helpers gerais
│
├── dashboard.py             # Dashboard Streamlit (gráficos / KPIs)
├── run_all.py               # Executa Flask + Streamlit juntos
│
├── data/
│   ├── raw/
│   ├── staging/
│   ├── curated/
│   ├── tasks.csv
│   ├── finance.csv
│   └── personal_analytics.db
│
└── README.md
```

---

# 🚀 Funcionalidades Principais

### ✔ ETL Completo
- Importa `tasks.csv` e `finance.csv`
- Normaliza, limpa, remove duplicados
- Gera tabelas no SQLite automaticamente

### ✔ CLI de Produtividade e Finanças

Exemplos:

```
python -m app.main etl
python -m app.main report --period all
python -m app.main prod --period 7d
python -m app.main fin --period 30d
```

### ✔ Machine Learning  
Usa **Linear Regression** para prever gastos futuros:

- Entrada: histórico do CSV ou banco
- Saída: projeção financeira

### ✔ Dashboard (Streamlit)
```
streamlit run dashboard.py
```

Exibe:

- Gastos por categoria  
- Horas por atividade  
- Tarefas por dia  
- Linha do tempo de produtividade  
- Previsão automática

### ✔ Interface Web (Flask)
```
flask --app app.web run
```

Inclui:

- Formulário para criar tasks  
- Formulário para despesas  
- Listar tasks  
- Listar despesas  
- API JSON

Endpoints:

```
/api/tasks
/api/expenses
/api/summary
```

### ✔ Executar Tudo Junto  
```
python run_all.py
```
Isso abre Streamlit e Flask simultaneamente.

---

# 📂 Formato dos CSVs

## ✅ tasks.csv
| external_id | title        | category      | completed_at          | duration_minutes |
|-------------|--------------|---------------|------------------------|------------------|
| 1           | Estudar IA   | estudos       | 2025-01-01 09:00:00    | 60               |

Categorias aceitas:
```
pessoal, profissional, estudos, saude
```

---

## ✅ finance.csv
| date       | category     | description     | amount  |
|------------|--------------|-----------------|---------|
| 2025-01-01 | mercado      | compra mensal   | 320.50  |

Categorias aceitas:
```
alimentacao, transporte, assinaturas, mercado, lazer, saude, outros
```

---

# 🔧 Instalação e Configuração

## 1 — Criar venv
```
python -m venv .venv
```

## 2 — Ativar
Windows:
```
.venv\Scripts\activate
```

## 3 — Instalar dependências
```
pip install -r requirements.txt
```

---

# 🧪 Rodando o ETL
```
python -m app.main etl
```

---

# 📊 Relatórios via CLI

### Relatório completo:
```
python -m app.main report --period all
```

### Somente produtividade:
```
python -m app.main prod --period all
```

### Somente finanças:
```
python -m app.main fin --period all
```

---

# 🌐 Interface Web (Flask)

### Rodar:
```
flask --app app.web run
```

### Acessar:
- http://localhost:5000/
- /tasks
- /expenses
- /task/new
- /expense/new
- /api/tasks
- /api/expenses
- /api/summary

---

# 📺 Dashboard (Streamlit)

### Rodar:
```
streamlit run dashboard.py
```

Inclui:

- KPIs de produtividade  
- KPIs financeiros  
- Gráficos dinâmicos  
- Previsões ML  
- Tabelas filtráveis  

---

# 🧩 Integrando com Airflow (Opcional)

Crie uma DAG em:

`airflow/dags/personal_analytics_dag.py`

Exemplo:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG("personal_analytics", start_date=datetime(2025,1,1), schedule="@daily"):
    etl = BashOperator(
        task_id="etl",
        bash_command="cd /path/to/project && .venv/Scripts/activate && python -m app.main etl"
    )
```

---

# 📁 Explicação dos Arquivos

### `etl.py`
- Lê os CSVs
- Valida
- Normaliza
- Insere no SQLite

### `models.py`
- Define Task, Expense e TimeLog
- Cria tabelas automaticamente

### `analytics.py`
- KPIs de produtividade
- Gasto por categoria
- Horas totais
- Tempo médio por atividade

### `ml.py`
- Previsão de gastos  
- Modelo Linear Regression

### `web.py`
- Formulários HTML
- API JSON
- Tabelas formatadas

### `dashboard.py`
- UI Streamlit  
- KPIs
- Gráficos
- Previsões

### `run_all.py`
- Flask + Streamlit simultâneos

---

# ➕ Como adicionar dados ao CSV

```python
import csv
from datetime import datetime

def add_task(title, category, minutes):
    with open("data/tasks.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            datetime.now().timestamp(),
            title,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            minutes
        ])
```

---

# 🤝 Contribuindo
- Melhorar dashboards
- Criar novos modelos ML
- Adicionar categorização automática
- Criar notificações
- Criar API pública

---

# 📜 Licença
MIT — livre para uso pessoal e profissional.

---
