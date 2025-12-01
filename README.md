# 📊 Personal Productivity Analytics
### *Sistema completo de produtividade + finanças – ETL, ML, Web, Dashboard e CLI.*

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Pandas](https://img.shields.io/badge/Pandas-ETL-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-yellow)
![Flask](https://img.shields.io/badge/Web-API-red)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-pink)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

# 🇧🇷 Versão em Português

## 📘 Sobre o Projeto
O **Personal Productivity Analytics** é um sistema pessoal que integra:

- Produtividade (tarefas, tempo, categorias)
- Controle financeiro (despesas, categorias, totais)
- ETL estruturado com SQLite
- Previsões financeiras com Machine Learning
- Dashboard interativo via Streamlit
- API Web + interface em Flask
- Automação completa via CLI

---

## 📐 Arquitetura

```
personal-productivity-analytics/
│
├── app/
│   ├── etl.py
│   ├── models.py
│   ├── ml.py
│   ├── report.py
│   ├── main.py
│   ├── web.py
│   ├── config.py
│   └── utils.py
│
├── data/
│   ├── tasks.csv
│   ├── finance.csv
│   └── productivity.db
│
├── dashboard.py
├── README.md
└── requirements.txt
```

---

## 🚀 Funcionalidades
✔ ETL completo  
✔ Relatórios CLI  
✔ Previsões (ML)  
✔ Dashboard (Streamlit)  
✔ Web/API (Flask)  
✔ Base de dados SQLite  

---

## 📂 Formato dos CSVs

### **tasks.csv**

| external_id | title | category | completed_at | duration_minutes |
|-------------|--------|----------|--------------|------------------|

Categorias:
```
pessoal, profissional, saude, estudos, familia, financeiro
```

### **finance.csv**

| date | category | description | amount |
|------|----------|-------------|--------|

Categorias:
```
alimentacao, transporte, assinaturas, mercado, lazer, saude, outros
```

---

## 🔧 Como Rodar

### Criar ambiente
```
python -m venv .venv
```

### Ativar
```
.venv\Scripts\activate
```

### Instalar libs
```
pip install -r requirements.txt
```

### Rodar ETL
```
python -m app.main etl
```

### Dashboard
```
streamlit run dashboard.py
```

### Web
```
flask --app app.web run
```

---

# 🇺🇸 English Version

## 📘 About the Project
**Personal Productivity Analytics** is a unified personal data platform integrating:

- Productivity tracking (tasks, categories, durations)
- Financial tracking (expenses, categories, totals)
- ETL pipeline using SQLite
- Machine Learning forecasting
- Streamlit dashboard
- Web/API using Flask
- CLI automation for daily routines

---

## 📐 Architecture

```
personal-productivity-analytics/
│
├── app/
│   ├── etl.py
│   ├── models.py
│   ├── ml.py
│   ├── report.py
│   ├── main.py
│   ├── web.py
│   ├── config.py
│   └── utils.py
│
├── data/
│   ├── tasks.csv
│   ├── finance.csv
│   └── productivity.db
│
├── dashboard.py
└── requirements.txt
```

---

## 🚀 Features
✔ Full ETL pipeline  
✔ CLI reports  
✔ Machine Learning forecasts  
✔ Streamlit dashboard  
✔ Flask Web/API  
✔ SQLite storage  

---

## 📂 CSV Format

### **tasks.csv**

| external_id | title | category | completed_at | duration_minutes |
|-------------|--------|----------|--------------|------------------|

Categories:
```
personal, professional, health, study, family, financial
```

### **finance.csv**

| date | category | description | amount |
|------|----------|-------------|--------|

Categories:
```
food, transport, subscriptions, groceries, leisure, health, other
```

---

## 🔧 How to Run

### Create environment
```
python -m venv .venv
```

### Activate
```
.venv\Scripts\activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Run ETL
```
python -m app.main etl
```

### Run dashboard
```
streamlit run dashboard.py
```

### Run web server
```
flask --app app.web run
```

---

## 📜 License
MIT — free for personal and professional use.
