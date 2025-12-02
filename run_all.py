import subprocess
import time
import os
import signal
import sys

# Comandos para executar os serviços
FLASK_CMD = "flask --app app.web run --port 5000"
STREAMLIT_CMD = "streamlit run dashboard.py --server.port 8501"

processes = []


def run_process(command):
    """
    Executa um comando em subprocesso e retorna o processo.
    """
    return subprocess.Popen(command, shell=True)


def main():
    print("\n🚀 Iniciando serviços do Personal Productivity Analytics...\n")

    # Ativa o ambiente virtual automaticamente, se possível
    venv_path = os.path.join(".venv", "Scripts", "activate")
    if os.path.exists(venv_path):
        print("🔧 Ambiente virtual detectado. Lembre-se de ativá-lo antes de rodar este script.\n")

    # --- INICIAR FLASK ---
    print("🌐 Iniciando Flask (porta 5000)...")
    flask_proc = run_process(FLASK_CMD)
    processes.append(flask_proc)

    # Delay para garantir que o Flask inicia antes do Streamlit
    time.sleep(2)

    # --- INICIAR STREAMLIT ---
    print("📊 Iniciando Streamlit (porta 8501)...")
    streamlit_proc = run_process(STREAMLIT_CMD)
    processes.append(streamlit_proc)

    print("\n✔ Flask + Streamlit estão rodando!")
    print("   👉 Flask:      http://127.0.0.1:5000")
    print("   👉 Dashboard:  http://127.0.0.1:8501")
    print("\nPressione CTRL+C para encerrar ambos.\n")

    try:
        # Fica aguardando ambos processos
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando processos...")
        for p in processes:
            p.terminate()

        print("✔ Todos os serviços foram finalizados. Até a próxima!")
        sys.exit(0)


if __name__ == "__main__":
    main()
