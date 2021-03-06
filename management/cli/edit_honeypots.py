import getpass
import json
import os
import subprocess
import sys
import time

import click
import trio
from PyInquirer import prompt
from utilities import EmptyValidator
from utilities import hostdata
from utilities import hosts
from utilities import hostselector
from utilities import log
from utilities import setupConfig
from utilities import style
from utilities import writeConfig

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, "../../honeypots/honeypot/")
from ConfigTunnel import ConfigTunnel  # noqa: E402

config = setupConfig()


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def starthoneypot(ctx, selected_hosts=None):
    """
    Start a honeypot
    """

    if not config.has_option("GENERAL", "db"):
        db = None
        try:
            db = prompt(
                [
                    {
                        "type": "input",
                        "name": "db",
                        "message": "Database URL:",
                        "validate": EmptyValidator,
                    }
                ],
                style=style(),
            )["db"]
        except EOFError:
            log("Action cancelled by user", "red")
            return

        config.set("GENERAL", "db", db)
        writeConfig("Database URL " + db + " saved!")

    db = config.get("GENERAL", "db")

    if len(selected_hosts) == 0:
        selected_hosts = hostselector(
            "Which host(s) do you want to start a honeypot on?"
        )

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]
            status = host_data["status"]

            if installed == "False":
                log(host + " did not have an installed honeypot.", "red")
                continue

            if status == "active":
                log(host + " is already running a honeypot.", "red")
                continue

            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            ssh_port = host_data["ssh_port"]

            password = None
            try:
                password = prompt(
                    [
                        {
                            "type": "password",
                            "name": "password",
                            "message": ("Password for " + user + "@" + ip + ":"),
                        }
                    ],
                    style=style(),
                )["password"]
            except EOFError:
                log("Action cancelled by user", "red")
                continue

            stdout, stderr = subprocess.Popen(
                ["deployment/start.sh", ssh_key, ip, user, password, db, ssh_port],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            output = str(stdout.decode() + stderr.decode())
            log(output, "yellow")

            if "Honeypot started successfully" in output:
                host_data["status"] = "active"
                host_value = str(host_data)
                config.set("HOSTS", host, host_value)
                writeConfig(host + " is now running a honeypot.")
            else:
                log(host + " failed to start a honeypot.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def stophoneypot(ctx, selected_hosts=None):
    """
    Stop a honeypot
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector(
            "Which host(s) do you want to stop a honeypot on?"
        )

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]
            status = host_data["status"]

            if installed == "False":
                log(host + " did not have an installed honeypot.", "red")
                continue

            if status == "inactive":
                log(host + " was not running a honeypot.", "red")
                continue

            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            ssh_port = host_data["ssh_port"]

            password = None
            try:
                password = prompt(
                    [
                        {
                            "type": "password",
                            "name": "password",
                            "message": ("Password for " + user + "@" + ip + ":"),
                        }
                    ],
                    style=style(),
                )["password"]
            except EOFError:
                log("Action cancelled by user", "red")
                continue

            stdout, stderr = subprocess.Popen(
                ["deployment/stop.sh", ssh_key, ip, user, password, ssh_port],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            output = str(stdout.decode() + stderr.decode())
            log(output, "yellow")

            if "Honeypot stopped successfully" in output:
                host_data["status"] = "inactive"
                host_value = str(host_data)
                config.set("HOSTS", host, host_value)
                writeConfig("The honeypot on " + host + " is now stopped.")
            else:
                log("The honeypot on " + host + " failed to stop.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def configurehoneypot(ctx, selected_hosts=None):
    """
    Configure a honeypot through a live ConfigTunnel connection
    """
    selected_hosts = (
        hostselector("Which host(s) do you want to configure?")
        if len(selected_hosts) == 0
        else 0
    )

    if len(selected_hosts) == 0:
        log("No host has been selected.", "red")
        return

    choice = None
    try:
        choice = prompt(
            [
                {
                    "type": "list",
                    "name": "choice",
                    "message": "What do you need to do?",
                    "choices": ["Edit Configuration Files", "Reconfigure"],
                    "filter": lambda val: val.lower(),
                }
            ],
            style=style(),
        )["choice"]
    except EOFError:
        log("Action cancelled by user", "red")
        return

    if choice == "edit configuration files":
        all_hosts = hosts()

        for host in selected_hosts:
            if host in all_hosts:
                host_data = hostdata(host)
                user = host_data["user"]
                ip = host_data["ip"]
                ssh_key = host_data["ssh_key"]
                ssh_port = host_data["ssh_port"]

                # TODO: fix path if install path is static
                path = "~"
                cmd = (
                    'ssh -i {} -t {}@{} -p {} "cd {}; ls; '
                    'echo "Welcome to {}! Feel free to use your editor of choice to '
                    "edit the above configuration files, and run exit to return to "
                    'the CLI."; bash"'
                ).format(ssh_key, user, ip, ssh_port, path, host)

                print("\n")
                os.system(cmd)
            else:
                log("Host " + host + " could not be found.", "red")

    elif choice == "reconfigure":
        try:
            subchoice = prompt(
                [
                    {
                        "type": "list",
                        "name": "subchoice",
                        "message": "What do you need to do?",
                        "choices": [
                            "Reconfigure Sniffer",
                            "Reconfigure Ports",
                            "Reconfigure Sniffer and Ports",
                        ],
                        "filter": lambda val: val.lower(),
                    }
                ],
                style=style(),
            )["subchoice"]
        except EOFError:
            log("Action cancelled by user", "red")
            return

        message = {
            "reconfigure sniffer": "reconfigure sniff",
            "reconfigure ports": "reconfigure ports",
            "reconfigure sniffer and ports": "reconfigure sniff ports",
        }[subchoice]

        all_hosts = hosts()

        for host in selected_hosts:
            if host in all_hosts:
                host_data = hostdata(host)
                ip = host_data["ip"]
                # TODO: make this read from configs
                certfile = "../../config/cert.pem"
                confport = 9998
                try:

                    async def attempt_remote_config():
                        with trio.move_on_after(10):
                            async with trio.open_nursery() as nursery:
                                tunnel = ConfigTunnel(
                                    "client", confport, ip, cafile=certfile
                                )
                                await nursery.start(tunnel.connect)
                                await tunnel.send(
                                    message + " user " + getpass.getuser()
                                )
                                log("Ran '" + message + "' on " + host, "green")
                                await tunnel.destroy(nursery.cancel_scope)
                        log("Conftunnel timeout hit", "green")

                    trio.run(attempt_remote_config)
                except Exception as ex:
                    log("Could not connect to " + host, "red")
                    raise (ex)
            else:
                log("Host " + host + " could not be found.", "red")
