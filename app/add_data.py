# app/add_data.py
import csv
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

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

TIMELOG_LABELS = [
    "deep_work",
    "reuniao",
    "admin",
    "pesquisa",
    "codando",
    "foco",
]


def ensure_file_with_header(path: Path, header: list[str]):
    """Garante que o arquivo exista com o cabeçalho informado."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def get_next_task_id(tasks_path: Path) -> int:
    """Lê tasks.csv e retorna o próximo ID inteiro."""
    if not tasks_path.exists():
        return 1

    last_id = 0
    with tasks_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                last_id = max(last_id, int(row["id"]))
            except Exception:
                continue
    return last_id + 1


def _input_datetime(prompt: str, default_now: bool = True) -> str:
    """
    Pede uma data/hora no formato YYYY-MM-DD HH:MM.
    Se usuário der enter, usa agora se default_now=True.
    Repete até ser válido.
    """
    while True:
        value = input(prompt + " (YYYY-MM-DD HH:MM) [enter = agora]: ").strip()
        if not value and default_now:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if value:
            try:
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("⚠️ Formato inválido. Exemplo válido: 2025-01-10 18:30")
        else:
            print("⚠️ Entrada vazia. Tente novamente.")


def _input_date(prompt: str, default_today: bool = True) -> str:
    while True:
        value = input(prompt + " (YYYY-MM-DD) [enter = hoje]: ").strip()
        if not value and default_today:
            return datetime.now().strftime("%Y-%m-%d")
        if value:
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                print("⚠️ Formato inválido. Exemplo válido: 2025-01-10")
        else:
            print("⚠️ Entrada vazia. Tente novamente.")


def _input_int(prompt: str, default: int) -> int:
    while True:
        value = input(f"{prompt} [padrão = {default}]: ").strip()
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            print("⚠️ Digite um número inteiro válido.")


def _input_float(prompt: str, default: float) -> float:
    while True:
        value = input(f"{prompt} [padrão = {default}]: ").strip().replace(",", ".")
        if not value:
            return default
        try:
            return float(value)
        except ValueError:
            print("⚠️ Digite um número válido (ex: 45.90).")


def _input_choice(prompt: str, options: list[str], default: str | None = None) -> str:
    """
    Mostra as opções aceitas e só retorna quando o usuário escolher uma válida.
    """
    opts_str = ", ".join(options)
    if default and default in options:
        base_prompt = f"{prompt} ({opts_str}) [padrão = {default}]: "
    else:
        base_prompt = f"{prompt} ({opts_str}): "

    while True:
        value = input(base_prompt).strip().lower()
        if not value and default and default in options:
            return default
        if value in options:
            return value
        print(f"⚠️ Opção inválida. Escolha uma das: {opts_str}")


# -------------------------
# ADD TASK
# -------------------------
def add_task():
    tasks_path = DATA_RAW / "tasks.csv"
    header = ["id", "title", "category", "completed_at", "duration_minutes"]
    ensure_file_with_header(tasks_path, header)

    next_id = get_next_task_id(tasks_path)
    print(f"\n📝 Adicionando TASK (id sugerido: {next_id})")

    title = input("Título da tarefa: ").strip() or "Tarefa sem título"
    category = _input_choice("Categoria da tarefa", TASK_CATEGORIES, default="pessoal")
    completed_at = _input_datetime("Data/hora de conclusão")
    duration = _input_int("Duração em minutos", 30)

    row = {
        "id": str(next_id),
        "title": title,
        "category": category,
        "completed_at": completed_at,
        "duration_minutes": str(duration),
    }

    with tasks_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(row)

    print("✅ Task adicionada!")


# -------------------------
# ADD TIME LOG
# -------------------------
def add_timelog():
    path = DATA_RAW / "timelog.csv"
    header = ["task_label", "project", "started_at", "ended_at", "duration_minutes"]
    ensure_file_with_header(path, header)

    print("\n⏱️ Adicionando TIMELOG")

    task_label = _input_choice("Tipo de atividade", TIMELOG_LABELS, default="deep_work")
    project = input("Projeto (Trabalho/Estudos/Portfolio...): ").strip() or "Trabalho"

    start_str = _input_datetime("Início")
    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")

    end_str_raw = input("Fim (YYYY-MM-DD HH:MM) [enter = +60min]: ").strip()
    if end_str_raw:
        try:
            end_dt = datetime.strptime(end_str_raw, "%Y-%m-%d %H:%M")
        except ValueError:
            print("⚠️ Formato inválido, usando +60min.")
            end_dt = start_dt + timedelta(minutes=60)
    else:
        end_dt = start_dt + timedelta(minutes=60)

    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    duration = int((end_dt - start_dt).total_seconds() / 60)

    row = {
        "task_label": task_label,
        "project": project,
        "started_at": start_str,
        "ended_at": end_str,
        "duration_minutes": str(duration),
    }

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(row)

    print("✅ TimeLog adicionado!")


# -------------------------
# ADD EXPENSE
# -------------------------
def add_expense():
    path = DATA_RAW / "expenses.csv"
    header = ["date", "category", "description", "amount"]
    ensure_file_with_header(path, header)

    print("\n💰 Adicionando DESPESA")

    date_str = _input_date("Data da despesa")
    category = _input_choice("Categoria da despesa", EXPENSE_CATEGORIES, default="outros")
    desc = input("Descrição: ").strip() or "Sem descrição"
    amount = _input_float("Valor (R$)", 0.0)

    row = {
        "date": date_str,
        "category": category,
        "description": desc,
        "amount": f"{amount:.2f}",
    }

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(row)

    print("💰 Despesa adicionada!")
