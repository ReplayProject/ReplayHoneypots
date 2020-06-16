from utilities import (
    log,
    style,
    hostselector,
    setupConfig,
    writeConfig,
    hosts,
    hostdata,
    DeviceIPValidator,
    EmptyValidator,
    FilePathValidator,
    HostnameValidator,
    PortValidator,
)
from PyInquirer import prompt
import click
import json
import subprocess

config = setupConfig()


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)


@main.command()
@click.pass_context
def addhost(ctx):
    """
    Add a host
    """

    new_host = None
    try:
        new_host = prompt(
            [
                {
                    "type": "input",
                    "name": "hostname",
                    "message": "Hostname:",
                    "validate": HostnameValidator,
                },
                {
                    "type": "input",
                    "name": "user",
                    "message": "Username:",
                    "validate": EmptyValidator,
                },
                {
                    "type": "input",
                    "name": "ip",
                    "message": "IP Address:",
                    "validate": DeviceIPValidator,
                },
                {
                    "type": "input",
                    "name": "ssh_port",
                    "message": "Port:",
                    "validate": PortValidator,
                },
                {
                    "type": "input",
                    "name": "ssh_key",
                    "message": "SSH Key:",
                    "validate": FilePathValidator,
                },
            ],
            style=style(),
        )
    except EOFError:
        log("Action cancelled by user", "red")
        return

    hostname = new_host.pop("hostname")
    new_host["status"] = "inactive"
    new_host["installed"] = "False"
    host_value = str(new_host)
    config.set("HOSTS", hostname, host_value)
    writeConfig("New host " + hostname + " saved!")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def removehost(ctx, selected_hosts=None):
    """
    Remove a host
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector("Which host(s) do you want to remove?")

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data["installed"]

            if installed == "True":
                log(
                    host
                    + " has a honeypot installed. To uninstall this honeypot, select 'Uninstall Honeypot' command.",
                    "red",
                )
                continue

            removed = config.remove_option("HOSTS", host)

            if removed:
                writeConfig(host + " has been removed.")
            else:
                log(host + " could not be removed.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option("-h", "--hosts", "selected_hosts", multiple=True)
@click.pass_context
def checkstatus(ctx, selected_hosts=None):
    """
    Check the status of hosts
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector("Which host(s) do you want to check?")

        if len(selected_hosts) == 0:
            log("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            user = host_data["user"]
            ip = host_data["ip"]
            ssh_key = host_data["ssh_key"]
            ssh_port = host_data["ssh_port"]

            stdout, stderr = subprocess.Popen(
                ["ssh", "-i", ssh_key, (user + "@" + ip), "-p", ssh_port, "uname -a"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()

            if stderr:
                log(
                    "Error while connecting to "
                    + user
                    + "@"
                    + ip
                    + " using SSH key "
                    + ssh_key
                    + ": "
                    + stderr.decode(),
                    "red",
                )

            log(stdout.decode(), "green")
        else:
            log("Host " + host + " could not be found.", "red")
