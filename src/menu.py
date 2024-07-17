import subprocess
import os
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from typing import List, Callable, Optional, Tuple
import logging

from src.fix_client import FIXClient

console = Console()
running = True

# Configure logger
logging.basicConfig(filename='application.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main_menu(*clients: List['FIXClient']) -> None:
    """
    Displays the main menu and handles user interactions.
    
    Args:
        clients (List[FIXClient]): List of FIXClient instances.
    """
    menu_options: dict[str, Tuple[str, Callable[[], None]]] = {
        "1": ("Logon", lambda: logon_clients(clients)),
        "2": ("Send ResendRequest", lambda: send_resend_request_to_clients(clients)),
        "3": ("Logout and exit", lambda: logout_clients(clients))
    }

    while running:
        try:
            console.clear()
            display_menu(menu_options)
            choice: str = Prompt.ask("\n[bold cyan]Enter your choice[/bold cyan]", choices=list(menu_options.keys()), default="1")
            menu_options[choice][1]()
            if choice == "3":
                break
        except Exception as e:
            logging.error(f"An error occurred in the main menu: {e}")
            console.print(Panel(f"[red]An error occurred: {e}[/red]", title="Error", border_style="red"))
            console.input("Press ENTER to continue...")

def display_menu(menu_options: dict[str, Tuple[str, Callable[[], None]]]) -> None:
    """
    Displays the main menu using a table format.
    
    Args:
        menu_options (dict[str, Tuple[str, Callable[[], None]]]): Dictionary of menu options and their descriptions.
    """
    console.rule("[bold blue]MAIN MENU[/bold blue]")

    table: Table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", justify="center", style="cyan", no_wrap=True)
    table.add_column("Description", justify="left", style="magenta")

    for key, (description, _) in menu_options.items():
        table.add_row(key, description)

    console.print(table)

def logon_clients(clients: List['FIXClient']) -> None:
    """
    Logs on all clients.
    
    Args:
        clients (List[FIXClient]): List of FIXClient instances.
    """
    console.clear()
    try:
        for client in clients:
            client.logon()
        console.print(Panel("[green]All clients logged on successfully.[/green]", title="Success", border_style="green"))
    except Exception as e:
        logging.error(f"An error occurred during logon: {e}")
        console.print(Panel(f"[red]An error occurred during logon: {e}[/red]", title="Error", border_style="red"))
    finally:
        console.input("Press ENTER to continue...")

def send_resend_request_to_clients(clients: List['FIXClient']) -> None:
    """
    Sends a ResendRequest to all clients.
    
    Args:
        clients (List[FIXClient]): List of FIXClient instances.
    """
    console.clear()
    try:
        begin_seq_no: int = int(Prompt.ask("Enter BeginSeqNo:", default="1"))
        end_seq_no: int = int(Prompt.ask("Enter EndSeqNo (0 for all subsequent messages):", default="0"))
        for client in clients:
            client.send_resend_request(begin_seq_no, end_seq_no)
        console.print(Panel("[green]ResendRequest sent to all clients.[/green]", title="Success", border_style="green"))
    except Exception as e:
        logging.error(f"An error occurred while sending ResendRequest: {e}")
        console.print(Panel(f"[red]An error occurred while sending ResendRequest: {e}[/red]", title="Error", border_style="red"))
    finally:
        console.input("Press ENTER to continue...")

def logout_clients(clients: List['FIXClient']) -> None:
    """
    Logs out all clients.
    
    Args:
        clients (List[FIXClient]): List of FIXClient instances.
    """
    console.clear()
    try:
        for client in clients:
            client.logout()
        console.print(Panel("[green]All clients logged out successfully.[/green]", title="Success", border_style="green"))
    except Exception as e:
        logging.error(f"An error occurred during logout: {e}")
        console.print(Panel(f"[red]An error occurred during logout: {e}[/red]", title="Error", border_style="red"))
    finally:
        global running
        running = False
        console.input("Press ENTER to exit...")
        sys.exit(0)

if __name__ == "__main__":
    console.print("[bold red]This module should not be run directly. It is meant to be imported and used in main.py.[/bold red]")
