import os
import subprocess
import time

# Nome del processo Python da terminare
process_name = "main.py"

# Percorso del repository Git (sostituisci con il tuo percorso)
repo_path = "/home/dexter/telegram-kali-rpi"

while True:
    # Termina il processo Python se è in esecuzione
    for line in os.popen("ps aux | grep " + process_name + " | grep -v grep"):
        fields = line.split()
        pid = fields[1]
        os.kill(int(pid), 9)
        print("Processo Python terminato con PID:", pid)

    # Esegui il pull dal repository Git
    try:
        git_pull = subprocess.Popen(["git", "-C", repo_path, "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_pull.communicate()
        if git_pull.returncode == 0:
            print("Pull eseguito con successo.")
        else:
            print("Errore durante il pull.")
    except Exception as e:
        print("Errore durante il pull:", str(e))

    # Avvia il processo Python
    try:
        python_process = subprocess.Popen(["python", os.path.join(repo_path, process_name)])
        print("Processo Python avviato con PID:", python_process.pid)
        python_process.wait()
        print("Processo Python terminato con codice di uscita:", python_process.returncode)
    except Exception as e:
        print("Errore durante l'avvio del processo Python:", str(e))

    # Attendi 30 secondi prima di riprovare
    time.sleep(30)
