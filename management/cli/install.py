import json
import subprocess

import click
from PyInquirer import prompt
from utilities import FilePathValidator
from utilities import hostdata
from utilities import hosts
from utilities import hostselector
from utilities import log
from utilities import setupConfig
from utilities import style
from utilities import writeConfig

config = setupConfig()


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def installhoneypot(ctx, selected_hosts=None):
    """
    Install a honeypot
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector(
            "Which host(s) do you want to install a honeypot on?"
        )

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    tar_file = None
    try:
        tar_file = prompt(
            [
                {
                    "type": "input",
                    "name": "tar_file",
                    "message": "Tar File:",
                    "validate": FilePathValidator,
                }
            ],
            style=style(),
        )["tar_file"]
    except EOFError:
        log("Action cancelled by user", "red")
        return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]

            if installed == "True":
                log(host + " already has an installed honeypot.", "red")
                continue

            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            ssh_port = host_data["ssh_port"]

            stdout, stderr = subprocess.Popen(
                ["deployment/install.sh", ssh_key, ip, user, tar_file, ssh_port],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            output = str(stdout.decode() + stderr.decode())
            log(output, "yellow")

            if "Honeypot installed successfully" in output:
                host_data["installed"] = "True"
                host_value = str(host_data)
                config.set("HOSTS", host, host_value)
                writeConfig(host + " now has an installed honeypot.")
            else:
                log(host + " failed to install a honeypot.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def uninstallhoneypot(ctx, selected_hosts=None):
    """
    Stop and uninstall a honeypot
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector(
            "Which host(s) do you want to uninstall a honeypot on?"
        )

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]

            if installed == "False":
                log(host + " did not have an installed honeypot.", "red")
                continue

            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            status = host_data["status"]
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
                [
                    "deployment/uninstall.sh",
                    ssh_key,
                    ip,
                    user,
                    password,
                    status,
                    ssh_port,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            output = str(stdout.decode() + stderr.decode())
            log(output, "yellow")

            if "Honeypot uninstalled successfully" in output:
                host_data["status"] = "inactive"
                host_data["installed"] = "False"
                host_value = str(host_data)
                config.set("HOSTS", host, host_value)
                writeConfig("The honeypot on " + host + " is now uninstalled.")
            else:
                log("The honeypot on " + host + " failed to uninstall.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def reinstallhoneypot(ctx, selected_hosts=None):
    """
    Stop and reinstall a honeypot
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector(
            "Which host(s) do you want to reinstall a honeypot on?"
        )

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    tar_file = None
    try:
        tar_file = prompt(
            [
                {
                    "type": "input",
                    "name": "tar_file",
                    "message": "Tar File:",
                    "validate": FilePathValidator,
                }
            ],
            style=style(),
        )["tar_file"]
    except EOFError:
        log("Action cancelled by user", "red")
        return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]

            if installed == "False":
                log(host + " did not have an installed honeypot.", "red")
                continue

            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            status = host_data["status"]
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
                [
                    "deployment/reinstall.sh",
                    ssh_key,
                    ip,
                    user,
                    password,
                    tar_file,
                    status,
                    ssh_port,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            output = str(stdout.decode() + stderr.decode())
            log(output, "yellow")

            if "Honeypot reinstalled successfully" in output:
                host_data["status"] = "inactive"
                host_value = str(host_data)
                config.set("HOSTS", host, host_value)
                writeConfig("The honeypot on " + host + " is now reinstalled.")
            else:
                log("The honeypot on " + host + " failed to reinstall.", "red")
        else:
            log("Host " + host + " could not be found.", "red")
