from utilities import log, style, hostselector, setupConfig, writeConfig, DeviceIPValidator, EmptyValidator, FilePathValidator, HostnameValidator
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
        new_host = prompt([
            {
                'type': 'input',
                'name': 'hostname',
                'message': 'Hostname:',
                'validate': HostnameValidator
            },
            {
                'type': 'input',
                'name': 'user',
                'message': 'Username:',
                'validate': EmptyValidator
            },
            {
                'type': 'input',
                'name': 'ip',
                'message': 'IP Address:',
                'validate': DeviceIPValidator
            },
            {
                'type': 'input',
                'name': 'ssh_key',
                'message': 'SSH Key:',
                'validate': FilePathValidator,
            },
        ], style=style())
    except EOFError: 
        log("Action cancelled by user", "red")
        return 

    hostname = new_host.pop("hostname")
    new_host["status"] = "inactive"
    new_host["installed"] = "False"
    host_value = str(new_host)
    config.set('HOSTS', hostname, host_value)
    writeConfig("New host " + hostname + " saved!")
    
@main.command()
@click.pass_context
def removehost(ctx):
    """
    Remove a host
    """

    honeypots = hostselector("Which host(s) do you want to remove?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return 
    
    hosts = config.items('HOSTS')

    for host in hosts: 
        if host[0] in honeypots: 
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']

            if installed == "True": 
                log(host[0] + " has a honeypot installed. To uninstall this honeypot, select 'Uninstall Honeypot' command.", "red")
                continue
                
            removed = config.remove_option('HOSTS', host[0])

            if removed: 
                writeConfig(host[0] + " has been removed.")
            else: 
                log(host[0] + " could not be removed.", "red")

@main.command()
@click.option('-i', '--identity', 'key_file', type=click.Path(exists=True, file_okay=True))
@click.pass_context
def checkstatus(ctx, key_file):
    """
    Check the status of hosts
    """

    selected_hosts = hostselector("Which host(s) do you want to check?")

    if len(selected_hosts) == 0:
        log ("No host has been selected.", "red")
        return

    all_hosts = config.items('HOSTS')

    for host in all_hosts:
        if host[0] in selected_hosts:
            host_data = json.loads(host[1].replace("\'", "\""))
            user = host_data['user']
            ip = host_data['ip']
            ssh_key = host_data['ssh_key']

            stdout, stderr = subprocess.Popen(['ssh', '-i', ssh_key, (user + '@' + ip), 'uname -a'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            if stderr: 
                log ("Error while connecting to " + user + "@" + ip + " using SSH key " + ssh_key + ": " + stderr.decode(), "red")

            log (stdout.decode(), "green")
