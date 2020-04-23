from utilities import log, style, hostselector, setupConfig, writeConfig, EmptyValidator
from PyInquirer import prompt
import click
import json
import subprocess
import getpass
import time
import sys
import os

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../honeypots/honeypot/')

from ConfigTunnel import ConfigTunnel

config = setupConfig()

@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)


@main.command()
@click.pass_context
def starthoneypot(ctx):
    """
    Start a honeypot
    """

    if not config.has_option("GENERAL", "db"):
        db = None
        try:
            db = prompt([
                {
                    'type': 'input',
                    'name': 'db',
                    'message': 'Database URL:',
                    'validate': EmptyValidator
                }
            ], style=style())['db']
        except EOFError:
            log("Action cancelled by user", "red")
            return

        config.set('GENERAL', 'db', db)
        writeConfig("Database URL " + db + " saved!")

    db = config.get('GENERAL', 'db')

    honeypots = hostselector("Which host(s) do you want to start a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    hosts = config.items('HOSTS')

    for host in hosts:
        if host[0] in honeypots:
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']
            status = host_data['status']

            if installed == "False":
                log (host[0] + " did not have an installed honeypot.", "red")
                continue

            if status == "active":
                log (host[0] + " is already running a honeypot.", "red")
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

            stdout, stderr = subprocess.Popen(['deployment/start.sh', ssh_key, ip, user, password, db],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            output = str(stdout.decode() + stderr.decode())
            log (output, "yellow")

            if "Honeypot started successfully" in output: 
                host_data['status'] = 'active'
                host_value = str(host_data)
                config.set('HOSTS', host[0], host_value)
                writeConfig(host[0] + " is now running a honeypot.")
            else: 
                log (host[0] + " failed to start a honeypot.", "red") 


@main.command()
@click.pass_context
def stophoneypot(ctx):
    """
    Stop a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to stop a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    hosts = config.items('HOSTS')

    for host in hosts:
        if host[0] in honeypots:
            host_data = json.loads(host[1].replace("\'", "\""))
            installed = host_data['installed']
            status = host_data['status']

            if installed == "False":
                log (host[0] + " did not have an installed honeypot.", "red")
                continue

            if status == "inactive":
                log (host[0] + " was not running a honeypot.", "red")
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

            stdout, stderr = subprocess.Popen(['deployment/stop.sh', ssh_key, ip, user, password],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

            output = str(stdout.decode() + stderr.decode())
            log (output, "yellow")

            if "Honeypot stopped successfully" in output: 
                host_data['status'] = 'inactive'
                host_value = str(host_data)
                config.set('HOSTS', host[0], host_value)
                writeConfig("The honeypot on " + host[0] + " is now stopped.")
            else: 
                log ("The honeypot on " + host[0] + " failed to stop.", "red")


@main.command()
@click.pass_context
def configurehoneypot(ctx):
    """
    Configure a honeypot through a live ConfigTunnel connection
    """

    honeypots = hostselector("Which host(s) do you want to configure?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
        return

    choice = None
    try:
        choice = prompt([
            {
                'type': 'list',
                'name': 'choice',
                'message': 'What do you need to do?',
                'choices':
                ['Edit Configuration Files',
                 'Reconfigure'],
                'filter': lambda val: val.lower()
            }
        ], style=style())['choice']
    except EOFError:
        log("Action cancelled by user", "red")
        return

    if choice == "edit configuration files":
        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                user = host_data['user']
                ip = host_data['ip']
                ssh_key = host_data['ssh_key']

                # TODO: fix path
                path = "~/dan/config"

                cmd = 'ssh -i {} -t {}@{} "cd {}; ls; echo "Welcome to {}! Feel free to use your editor of choice to edit the above configuration files, and run exit to return to the CLI."; bash"'.format(ssh_key, user, ip, path, host[0])

                print('\n')
                os.system(cmd)

    elif choice == "reconfigure":
        try:
            subchoice = prompt([
                {
                    'type': 'list',
                    'name': 'subchoice',
                    'message': 'What do you need to do?',
                    'choices':
                    ['Reconfigure Sniffer',
                     'Reconfigure Ports',
                     'Reconfigure Sniffer and Ports'],
                    'filter': lambda val: val.lower()
                }
            ], style=style())['subchoice']
        except EOFError:
            log("Action cancelled by user", "red")
            return

        if subchoice == "reconfigure sniffer":
            message = "reconfigure sniff"
        elif subchoice == "reconfigure ports":
            message = "reconfigure ports"
        elif subchoice == "reconfigure sniffer and ports":
            message = "reconfigure sniff ports"

        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                ip = host_data['ip']

                tunnel = ConfigTunnel('client', host=ip)
                tunnel.start()
                time.sleep(2)

                if not tunnel.ready:
                    log ("Could not connect to " + host[0], "red")
                else:
                    tunnel.send(message + " user " + getpass.getuser())
                    log ("Ran '" + message + "' on " + host[0], "green")

                tunnel.stop()
                tunnel.join()
