# src/menu.py
import qprompt
import subprocess
import os
import sys

running = True

def start_concat_logs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    concat_logs_path = os.path.join(current_dir, 'concat_logs.py')
    return subprocess.Popen(['python', concat_logs_path])

def stop_concat_logs(process):
    if process:
        process.terminate()
        process.wait()

def main_menu(*clients):
    concat_logs_process = None
    menu = qprompt.Menu()
    menu.add("1", "Logon", lambda: logon_clients(clients, concat_logs_process))
    menu.add("2", "Send ResendRequest", lambda: send_resend_request_to_clients(clients))
    menu.add("3", "Logout and exit", lambda: logout_clients(clients, concat_logs_process))

    while running:
        choice = menu.show(header="MAIN MENU", returns="desc")
        if choice == "Logout and exit":
            break

def logon_clients(clients, concat_logs_process):
    for client in clients:
        client.logon()
    if not concat_logs_process:
        concat_logs_process = start_concat_logs()
    qprompt.pause()

def send_resend_request_to_clients(clients):
    begin_seq_no = qprompt.ask_int("Enter BeginSeqNo:")
    end_seq_no = qprompt.ask_int("Enter EndSeqNo (0 for all subsequent messages):")
    for client in clients:
        client.send_resend_request(begin_seq_no, end_seq_no)
    qprompt.pause()

def logout_clients(clients, concat_logs_process):
    for client in clients:
        client.logout()
    stop_concat_logs(concat_logs_process)
    global running
    running = False
    sys.exit(0)

if __name__ == "__main__":
    print("This module should not be run directly. It is meant to be imported and used in main.py.")
