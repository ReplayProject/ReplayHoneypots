from utilities import log, style, hostselector, setupConfig, writeConfig, FilePathValidator
from PyInquirer import prompt
import click
import json
import subprocess

config = setupConfig()

@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)

#TODO
@main.command()
@click.pass_context
def installhoneypot(ctx):
    """
    Install a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to install a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    tar_file = None
    try:
        tar_file = prompt([
            {
                'type': 'input',
                'name': 'tar_file',
                'message': 'Tar File:',
                'validate': FilePathValidator
            }
        ], style=style())['tar_file']
    except EOFError:
        log("Action cancelled by user", "red")
        return

    hosts = config.items('HOSTS')

    for host in hosts:
        if host[0] in honeypots:
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']

            if installed == "True":
                log (host[0] + " already has an installed honeypot.", "red")
                continue

            user = host_data['user']
            ip = host_data['ip']
            ssh_key = host_data['ssh_key']

            password = None
            try:
                password = prompt([
                    {
                        'type': 'password',
                        'name': 'password',
                        'message': ('Password for ' + user + "@" + ip + ":"),
                    }
                ], style=style())['password']
            except EOFError:
                log("Action cancelled by user", "red")
                continue

            stdout, stderr = subprocess.Popen(['deployment/install.sh', ssh_key, ip, user, password, tar_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            print (("" + stdout.decode() + stderr.decode()))

            # TODO: check for errors, do not label host as installed if there were any errors with install
            host_data['installed'] = 'True'
            host_value = str(host_data)
            config.set('HOSTS', host[0], host_value)
            writeConfig(host[0] + " now has an installed honeypot.")


#TODO
@main.command()
@click.pass_context
def uninstallhoneypot(ctx):
    """
    Stop and uninstall a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to uninstall a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    hosts = config.items('HOSTS')

    for host in hosts:
        if host[0] in honeypots:
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']

            if installed == "False":
                log (host[0] + " did not have an installed honeypot.", "red")
                continue

            user = host_data['user']
            ip = host_data['ip']
            ssh_key = host_data['ssh_key']
            status = host_data['status']

            password = None
            try:
                password = prompt([
                    {
                        'type': 'password',
                        'name': 'password',
                        'message': ('Password for ' + user + "@" + ip + ":"),
                    }
                ], style=style())['password']
            except EOFError:
                log("Action cancelled by user", "red")
                continue

            stdout, stderr = subprocess.Popen(['deployment/uninstall.sh', ssh_key, ip, user, password, status],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            print (("" + stdout.decode() + stderr.decode()))

            # TODO: check for errors, do not label host as uninstalled if there were any errors with uninstall
            host_data['status'] = 'inactive'
            host_data['installed'] = 'False'
            host_value = str(host_data)
            config.set('HOSTS', host[0], host_value)
            writeConfig("The honeypot on " + host[0] + " is now uninstalled.")


#TODO
@main.command()
@click.pass_context
def reinstallhoneypot(ctx):
    """
    Stop and reinstall a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to reinstall a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    tar_file = None
    try:
        tar_file = prompt([
            {
                'type': 'input',
                'name': 'tar_file',
                'message': 'Tar File:',
                'validate': FilePathValidator
            }
        ], style=style())['tar_file']
    except EOFError:
        log("Action cancelled by user", "red")
        return

    hosts = config.items('HOSTS')

    for host in hosts:
        if host[0] in honeypots:
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']

            if installed == "False":
                log (host[0] + " did not have an installed honeypot.", "red")
                continue

            user = host_data['user']
            ip = host_data['ip']
            ssh_key = host_data['ssh_key']
            status = host_data['status']

            password = None
            try:
                password = prompt([
                    {
                        'type': 'password',
                        'name': 'password',
                        'message': ('Password for ' + user + "@" + ip + ":"),
                    }
                ], style=style())['password']
            except EOFError:
                log("Action cancelled by user", "red")
                continue

            stdout, stderr = subprocess.Popen(['deployment/reinstall.sh', ssh_key, ip, user, password, tar_file, status],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            print (("" + stdout.decode() + stderr.decode()))

            # TODO: check for errors, do not label host as inactive if there were any errors with redeployment
            host_data['status'] = 'inactive'
            host_value = str(host_data)
            config.set('HOSTS', host[0], host_value)
            writeConfig("The honeypot on " + host[0] + " is now reinstalled.")
