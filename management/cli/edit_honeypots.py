from utilities import log, style, hostselector, setupConfig, writeConfig, hosts, hostdata, EmptyValidator
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
@click.option('-h', '--hosts', 'selected_hosts', multiple=True)
@click.pass_context
def starthoneypot(ctx, selected_hosts=None):
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

    if len(selected_hosts) == 0:
        selected_hosts = hostselector("Which host(s) do you want to start a honeypot on?")

        if len(selected_hosts) == 0:
            log ("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data['installed']
            status = host_data['status']

            if installed == "False":
                log (host + " did not have an installed honeypot.", "red")
                continue

            if status == "active":
                log (host + " is already running a honeypot.", "red")
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
                config.set('HOSTS', host, host_value)
                writeConfig(host + " is now running a honeypot.")
            else:
                log (host + " failed to start a honeypot.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option('-h', '--hosts', 'selected_hosts', multiple=True)
@click.pass_context
def stophoneypot(ctx, selected_hosts=None):
    """
    Stop a honeypot
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector("Which host(s) do you want to stop a honeypot on?")

        if len(selected_hosts) == 0:
            log ("No host has been selected.", "red")
            return

    all_hosts = hosts()

    for host in selected_hosts:
        if host in all_hosts:
            host_data = hostdata(host)
            installed = host_data['installed']
            status = host_data['status']

            if installed == "False":
                log (host + " did not have an installed honeypot.", "red")
                continue

            if status == "inactive":
                log (host + " was not running a honeypot.", "red")
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
                config.set('HOSTS', host, host_value)
                writeConfig("The honeypot on " + host + " is now stopped.")
            else:
                log ("The honeypot on " + host + " failed to stop.", "red")
        else:
            log("Host " + host + " could not be found.", "red")


@main.command()
@click.option('-h', '--hosts', 'selected_hosts', multiple=True)
@click.pass_context
def configurehoneypot(ctx, selected_hosts=None):
    """
    Configure a honeypot through a live ConfigTunnel connection
    """

    if len(selected_hosts) == 0:
        selected_hosts = hostselector("Which host(s) do you want to configure?")

        if len(selected_hosts) == 0:
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
        all_hosts = hosts()

        for host in selected_hosts:
            if host in all_hosts:
                host_data = hostdata(host)
                user = host_data['user']
                ip = host_data['ip']
                ssh_key = host_data['ssh_key']

                # TODO: fix path if install path is static
                path = "~"

                cmd = 'ssh -i {} -t {}@{} "cd {}; ls; echo "Welcome to {}! Feel free to use your editor of choice to edit the above configuration files, and run exit to return to the CLI."; bash"'.format(ssh_key, user, ip, path, host)

                print('\n')
                os.system(cmd)
            else:
                log("Host " + host + " could not be found.", "red")

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

        all_hosts = hosts()

        for host in selected_hosts:
            if host in all_hosts:
                host_data = hostdata(host)
                ip = host_data['ip']

                tunnel = ConfigTunnel('client', host=ip)
                tunnel.start()
                time.sleep(2)

                if not tunnel.ready:
                    log ("Could not connect to " + host, "red")
                else:
                    tunnel.send(message + " user " + getpass.getuser())
                    log ("Ran '" + message + "' on " + host, "green")

                tunnel.stop()
                tunnel.join()
            else:
                log("Host " + host + " could not be found.", "red")
