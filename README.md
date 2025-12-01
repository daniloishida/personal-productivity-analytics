# 📊 Personal Productivity Analytics
### *Um sistema completo de produtividade + finanças – ETL, ML, Web, Dashboard e CLI.*

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Pandas](https://img.shields.io/badge/Pandas-ETL-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-yellow)
![Flask](https://img.shields.io/badge/Web-API-red)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-pink)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📘 Sobre o Projeto

O **Personal Productivity Analytics** é um sistema pessoal de produtividade criado para unificar:

- **tarefas**
- **tempo investido**
- **despesas e gastos**
- **previsões financeiras**
- **dashboard interativo**
- **API Web para inserir dados**
- **CLI para automação**
- **ETL completo estruturado**

---

## 📐 Arquitetura do Sistema

```
personal-productivity-analytics/
│
├── app/
│   ├── etl.py              # Lê CSVs e carrega para o SQLite
│   ├── models.py           # ORM SQLAlchemy - tabelas do banco
│   ├── ml.py               # Modelo de Machine Learning (previsão)
│   ├── report.py           # Relatórios agregados
│   ├── main.py             # CLI principal do sistema
│   ├── web.py              # Interface Web + API Flask
│   ├── config.py           # Caminhos e configuração global
│   └── utils.py            # Funções auxiliares
│
├── data/
│   ├── tasks.csv
│   ├── finance.csv
│   └── productivity.db     # Banco SQLite gerado pelo ETL
│
├── dashboard.py            # Dashboard em Streamlit
├── README.md               # Este arquivo ❤
└── requirements.txt        # Dependências
```

---

## 🚀 Funcionalidades

### ✔ ETL Completo
Importa os dados dos arquivos `tasks.csv` e `finance.csv` e carrega tudo no SQLite.

### ✔ Relatórios via CLI
```
python -m app.main report --period 30d
```

### ✔ Previsão com Machine Learning
Utiliza `LinearRegression` para prever gastos.

### ✔ Dashboard Streamlit
```
streamlit run dashboard.py
```

### ✔ Web Flask
```
flask --app app.web run
```

---

## 📂 Estrutura dos CSVs

### tasks.csv
| external_id | title | category | completed_at | duration_minutes |
|-------------|--------|----------|----------------|------------------|
| 1 | Limpar casa | pessoal | 2025-01-01 09:00:00 | 45 |

Categorias aceitas:
```
pessoal, profissional, saude, estudos, familia, financeiro
```

### finance.csv
| date | category | description | amount |
|-------|----------|-------------|--------|
| 2025-01-01 | mercado | Compra mensal | 320.50 |

Categorias aceitas:
```
alimentacao, transporte, assinaturas, mercado, lazer, saude, outros
```

---

## 🔧 Como Rodar o Projeto

### Criar ambiente virtual
```
python -m venv .venv
```

### Ativar
```
.venv\Scriptsctivate
```

### Instalar dependências
```
pip install -r requirements.txt
```

### Executar ETL
```
python -m app.main etl
```

---

## 📁 Explicação dos Arquivos

- **etl.py** → extrai, trata e carrega dados  
- **models.py** → ORM  
- **ml.py** → modelo de previsão  
- **report.py** → relatórios e KPIs  
- **main.py** → interface CLI  
- **web.py** → interface web e API  
- **dashboard.py** → dashboard Streamlit  

---

## 📜 Licença

MIT — livre para uso pessoal e profissional.
