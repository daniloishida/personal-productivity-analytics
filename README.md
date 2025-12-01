# 📊 Personal Productivity Analytics  
### *Um sistema completo de produtividade + finanças para uso pessoal – ETL, ML, Web, Dashboard e CLI.*

![badge](https://img.shields.io/badge/python-3.11+-blue)
![badge](https://img.shields.io/badge/pandas-etl-green)
![badge](https://img.shields.io/badge/sqlalchemy-database-orange)
![badge](https://img.shields.io/badge/scikit--learn-machine%20learning-yellow)
![badge](https://img.shields.io/badge/flask-web%20api-red)
![badge](https://img.shields.io/badge/streamlit-dashboard-pink)
![badge](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 📘 Sobre o Projeto

Este projeto nasceu como **um sistema pessoal de produtividade**, capaz de:

- Importar CSVs de produtividade e finanças  
- Carregar os dados em um **banco SQLite estruturado**  
- Gerar relatórios via **linha de comando (CLI)**  
- Criar **previsões de gastos com Machine Learning (Linear Regression)**  
- Exibir os dados em **dashboard Streamlit**  
- Inserir tarefas e despesas via **interface Web Flask**  
- Expor uma **API JSON** para integração com outras ferramentas  

Foi projetado para ser **útil** e **real**, não apenas um projeto técnico — algo que uma pessoa realmente usaria no dia a dia para se organizar.

---

# 📐 Arquitetura do Sistema

personal-productivity-analytics/
│
├── app/
│ ├── etl.py # Lê CSVs e carrega para o SQLite
│ ├── models.py # ORM SQLAlchemy - tabelas do banco
│ ├── ml.py # Modelo de Machine Learning (previsão)
│ ├── report.py # Relatórios agregados
│ ├── main.py # CLI principal do sistema
│ ├── web.py # Interface Web + API (Flask)
│ ├── config.py # Caminhos, configurações
│ └── utils.py # Funções auxiliares
│
├── data/
│ ├── tasks.csv
│ ├── finance.csv
│ └── productivity.db # Banco SQLite gerado pelo ETL
│
├── dashboard.py # Dashboard Analytics (Streamlit)
├── README.md # Este arquivo ❤
└── requirements.txt # Dependências

yaml
Copy code

---

# 🚀 Funcionalidades

### ✔ ETL completo  
Importa dados dos CSVs:  
- **tasks.csv**  
- **finance.csv**

Tudo vai para o banco SQLite usando SQLAlchemy.

### ✔ Relatórios via CLI  
Exemplo:

python -m app.main report --period 30d

shell
Copy code

### ✔ Previsão de gastos com Machine Learning  
Usando scikit-learn (Linear Regression).

### ✔ Dashboard Streamlit  
Rodar:

streamlit run dashboard.py

markdown
Copy code

### ✔ Interface Web Flask  
Permite cadastrar:

- **Tasks**
- **Despesas**

Rodar:

flask --app app.web run

yaml
Copy code

### ✔ API JSON  
Endpoints:

- `/api/tasks`
- `/api/expenses`

---

# 📂 Estrutura dos CSVs

## **tasks.csv**

| external_id | title        | category     | completed_at         | duration_minutes |
|-------------|--------------|--------------|------------------------|------------------|
| 1           | Limpar casa  | pessoal      | 2025-01-01 09:00:00    | 45               |

### Categorias aceitas:
pessoal
profissional
saude
estudos
familia
financeiro

yaml
Copy code

---

## **finance.csv**

| date       | category     | description         | amount |
|------------|--------------|----------------------|--------|
| 2025-01-01 | mercado      | Compra mensal        | 320.50 |

### Categorias aceitas:
alimentacao
transporte
assinaturas
mercado
lazer
saude
outros

yaml
Copy code

---

# 🔧 Como Rodar o Projeto

## 1 — Criar ambiente virtual
python -m venv .venv

shell
Copy code

## 2 — Ativar ambiente
.venv\Scripts\activate

shell
Copy code

## 3 — Instalar dependências
pip install -r requirements.txt

yaml
Copy code

---

# 🧪 Executando o ETL

python -m app.main etl

yaml
Copy code

Isso vai:

- Criar o banco SQLite  
- Carregar tasks  
- Carregar despesas  
- Preparar os dados para relatórios e dashboard  

---

# 📊 Gerando Relatórios

## Relatório completo:
python -m app.main report --period all

shell
Copy code

## Relatório financeiro:
python -m app.main fin --period 30d

shell
Copy code

## Relatório de produtividade:
python -m app.main prod --period 7d

yaml
Copy code

---

# 🌐 Interface Web

### Iniciar:

flask --app app.web run

markdown
Copy code

Acesse:

- `http://127.0.0.1:5000/` (Home)  
- `/task/new` – criar tasks  
- `/expense/new` – criar despesas  
- `/expenses` – listar despesas  
- `/api/tasks` – JSON  
- `/api/expenses` – JSON  

---

# 📺 Dashboard Analytics

Rodar:

streamlit run dashboard.py

markdown
Copy code

Funcionalidades:

- Gráficos de gastos  
- Gráficos de horas trabalhadas  
- Previsões  
- Tabelas filtráveis  

---

# 📁 Explicação dos Arquivos

### **etl.py**
- Lê CSVs  
- Normaliza dados  
- Remove duplicados  
- Aplica regras de negócio  
- Insere no SQLite  

### **models.py**
Define tabelas:
- Tasks  
- Expenses  
Usando SQLAlchemy ORM.

### **ml.py**
- Carrega dados do banco  
- Treina modelo Linear Regression  
- Estima gasto futuro  

### **report.py**
- Queries agregadas  
- Gasto por categoria  
- Tarefas concluídas  
- Tempo investido  

### **main.py**
CLI principal.  
Comandos:

etl
prod
fin
report
add-task
add-expense

python
Copy code

### **web.py**
- Formulário HTML  
- API JSON  
- Cadastro de Tasks  
- Cadastro de Despesas  

### **dashboard.py**
Interface Streamlit com gráficos.

---

# ➕ Como Adicionar Dados no CSV

Exemplo simples:

```python
from datetime import datetime
import csv

def add_task_csv(title, category, minutes):
    with open("data/tasks.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().timestamp(),
            title,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            minutes
        ])

add_task_csv("Estudar IA", "estudos", 50)
🤝 Contribuindo
Abrir issues

Sugerir funcionalidades

Criar dashboards extras

Integrar APIs externas

📜 Licença
MIT — livre para uso pessoal e profissional.