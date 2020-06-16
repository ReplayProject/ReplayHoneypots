#! /env/bin/python3

# https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df

from __future__ import print_function, unicode_literals
import os
import signal
import sys

from utilities import log, style, setupConfig, writeConfig
from PyInquirer import prompt
import click

config = setupConfig()


def signal_handler(sig, frame):
    writeConfig("Exiting the RePlay CLI...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@click.group()
@click.pass_context
def main(ctx):
    """
    Straightforward CLI for managing & deploying honeypots
    """
    ctx.ensure_object(dict)


from manage_hosts import addhost, removehost, checkstatus

main.add_command(addhost)
main.add_command(removehost)
main.add_command(checkstatus)

from install import installhoneypot, uninstallhoneypot, reinstallhoneypot

main.add_command(installhoneypot)
main.add_command(uninstallhoneypot)
main.add_command(reinstallhoneypot)

from edit_honeypots import starthoneypot, stophoneypot, configurehoneypot

main.add_command(starthoneypot)
main.add_command(stophoneypot)
main.add_command(configurehoneypot)


@main.command()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def start(ctx, debug):
    """
    Run this CLI in interactive mode
    """
    global config
    log("RePlay CLI", color="blue", figlet=True)
    log("Welcome to the RePlay CLI" + (" (DEBUGGING MODE)" if debug else ""), "green")
    log("To go back from a submenu, use Ctrl+D", "yellow")
    log("To force quit, use Ctrl+C", "red")

    ctx.invoke(main_menu)


"""
#####
Menus
#####
"""


@click.pass_context
def main_menu(ctx):
    # Main Loop to run the interactive menu
    while True:
        choice = prompt(
            [
                {
                    "type": "list",
                    "name": "choice",
                    "message": "What do you need to do?",
                    "choices": ["Manage Hosts", "Install", "Edit Honeypots", "Exit"],
                    "filter": lambda val: val.lower(),
                }
            ],
            style=style(),
        )["choice"]

        if choice == "manage hosts":
            ctx.invoke(manage_hosts_submenu)

        elif choice == "install":
            ctx.invoke(install_submenu)

        elif choice == "edit honeypots":
            ctx.invoke(edit_honeypots_submenu)

        elif choice == "exit":
            os.kill(os.getpid(), signal.SIGINT)


@click.pass_context
def manage_hosts_submenu(ctx):
    try:
        subchoice = prompt(
            [
                {
                    "type": "list",
                    "name": "subchoice",
                    "message": "What do you need to do?",
                    "choices": ["Add Host", "Remove Host", "Check Status"],
                    "filter": lambda val: val.lower(),
                }
            ],
            style=style(),
        )["subchoice"]
    except EOFError:
        ctx.invoke(main_menu)

    if subchoice == "add host":
        ctx.invoke(addhost)

    elif subchoice == "remove host":
        ctx.invoke(removehost)

    elif subchoice == "check status":
        ctx.invoke(checkstatus)


@click.pass_context
def install_submenu(ctx):
    try:
        subchoice = prompt(
            [
                {
                    "type": "list",
                    "name": "subchoice",
                    "message": "What do you need to do?",
                    "choices": [
                        "Install Honeypot",
                        "Uninstall Honeypot",
                        "Reinstall Honeypot",
                    ],
                    "filter": lambda val: val.lower(),
                }
            ],
            style=style(),
        )["subchoice"]
    except EOFError:
        ctx.invoke(main_menu)

    if subchoice == "install honeypot":
        ctx.invoke(installhoneypot)

    elif subchoice == "uninstall honeypot":
        ctx.invoke(uninstallhoneypot)

    elif subchoice == "reinstall honeypot":
        ctx.invoke(reinstallhoneypot)


@click.pass_context
def edit_honeypots_submenu(ctx):
    try:
        subchoice = prompt(
            [
                {
                    "type": "list",
                    "name": "subchoice",
                    "message": "What do you need to do?",
                    "choices": [
                        "Start Honeypot",
                        "Stop Honeypot",
                        "Configure Honeypot",
                    ],
                    "filter": lambda val: val.lower(),
                }
            ],
            style=style(),
        )["subchoice"]
    except EOFError:
        ctx.invoke(main_menu)

    if subchoice == "start honeypot":
        ctx.invoke(starthoneypot)

    elif subchoice == "stop honeypot":
        ctx.invoke(stophoneypot)

    elif subchoice == "configure honeypot":
        ctx.invoke(configurehoneypot)


if __name__ == "__main__":
    try:
        main()
    except KeyError:
        os.kill(os.getpid(), signal.SIGINT)
