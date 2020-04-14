
#! /env/bin/python3

# https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df

# Utilities
from __future__ import print_function, unicode_literals
import configparser
import os
import re
import sys
import six
import signal
import time
import itertools
import subprocess
import json
import ipaddress


# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../honeypots/honeypot/')


from ConfigTunnel import ConfigTunnel

# Interactivity
from PyInquirer import Token, ValidationError, Validator, print_json, prompt, style_from_dict, Separator
import click

# Look & Feel
from pprint import *
from pyfiglet import figlet_format

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})

# Configuration Setup
CONF_PATH = 'honeycli.cfg'
config = configparser.ConfigParser()


def setupConfig():
    # Open existing conf or start anew
    try:
        with open(CONF_PATH) as f:
            config.read_file(f)
    except IOError:
        pass

    # Setup required Sections of the configuration
    if not config.has_section('HOSTS'):
        config.add_section('HOSTS')
    if not config.has_section('GENERAL'):
        config.add_section('GENERAL')


setupConfig()

conf = config['GENERAL']


def writeConfig(message):
    with open(CONF_PATH, 'w') as f:
        config.write(f)
    log(message, "green")


def signal_handler(sig, frame):
    writeConfig('Exiting the RePlay CLI...')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def getContentType(answer, conttype):
    return answer.get("content_type").lower() == conttype.lower()


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)


@click.group()
@click.pass_context
def main(ctx):
    """
    Straightforward CLI for managing & deploying honeypots
    """
    ctx.ensure_object(dict)


"""
##########
Validators
##########
"""


"""
Validate an IP address based on:
1 - IP address value
2 - whether the IP address already exists in the CLI data
"""
class DeviceIPValidator(Validator):
    def validate(self, value):

        if len(value.text):
            try:
                valid_ip = ipaddress.ip_address(value.text)
            except ValueError as e:
                raise ValidationError(
                    message=str(e),
                    cursor_position=len(value.text))

            hosts = config.items('HOSTS')
            ip = []

            for host in hosts:
                data = json.loads(host[1].replace("\'", "\""))
                ip.append(data['ip'])

            if (value.text in ip):
                raise ValidationError(
                    message="A host with that IP address already exists. To replace it, please remove host first.",
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


"""
Validate a path based on if it is a file

Invalid paths include:
1 - folder paths
2 - file paths that the user does not have permission to access
3 - non-existent paths
"""
class FilePathValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if not os.path.isfile(value.text):
                raise ValidationError(
                    message=("File " + value.text + " could not be found"),
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


"""
Validate a hostname based on whether the hostname already exists in the CLI data
"""
class HostnameValidator(Validator):
    """
    Validate a hostname
    """
    def validate(self, value):

        if len(value.text):
            hosts = config.items('HOSTS')
            hostnames = []

            for host in hosts:
                hostnames.append(host[0])

            if (value.text in hostnames):
                raise ValidationError(
                    message="A host with that hostname already exists. To replace it, please remove host first.",
                    cursor_position=len(value.text))

        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


"""
############
CLI Commands
############
"""


@main.command()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def start(ctx, debug):
    """
    Run this CLI in interactive mode
    """
    global config
    log("RePlay CLI", color="blue", figlet=True)
    log("Welcome to the RePlay CLI" +
        (" (DEBUGGING MODE)" if debug else ""), "green")

    ctx.invoke(choices)


@click.pass_context
def choices(ctx):
    # Main Loop to run the interactive menu
    while True:

        try:
            choice = prompt([
                {
                    'type': 'list',
                    'name': 'choice',
                    'message': 'What do you need to do?',
                    'choices':
                    ['Add/Update Host', 
                     'View Host',
                     'Remove Host', 
                     'Exit'],
                    'filter': lambda val: val.lower()
                }
            ], style=style)['choice']
        except KeyError:
            os.kill(os.getpid(), signal.SIGINT)
        
        if choice == 'add/update host':
            try:
                subchoice = prompt([
                    {
                        'type': 'list',
                        'name': 'subchoice',
                        'message': 'What do you need to do?',
                        'choices':
                        ['Add Host',
                         'Start Honeypot',
                         'Reinstall Honeypot',
                         'Configure Honeypot'],
                        'filter': lambda val: val.lower()
                    }
                ], style=style)['subchoice']
            except KeyError:
                os.kill(os.getpid(), signal.SIGINT)

            if subchoice == 'add host':
                ctx.invoke(addhost)

            elif subchoice == 'start honeypot':
                ctx.invoke(starthoneypot)

            elif subchoice == 'reinstall honeypot':
                ctx.invoke(reinstallhoneypot) 

            elif subchoice == 'configure honeypot':
                ctx.invoke(configurehoneypot)

        elif choice == 'view host':
            try:
                subchoice = prompt([
                    {
                        'type': 'list',
                        'name': 'subchoice',
                        'message': 'What do you need to do?',
                        'choices':
                        ['Check Status'],
                        'filter': lambda val: val.lower()
                    }
                ], style=style)['subchoice']
            except KeyError:
                os.kill(os.getpid(), signal.SIGINT)

            if subchoice == 'check status':
                ctx.invoke(checkstatus) 

        elif choice == 'remove host':
            try:
                subchoice = prompt([
                    {
                        'type': 'list',
                        'name': 'subchoice',
                        'message': 'What do you need to do?',
                        'choices':
                        ['Remove Host',
                         'Stop Honeypot', 
                         'Uninstall Honeypot'],
                        'filter': lambda val: val.lower()
                    }
                ], style=style)['subchoice']
            except KeyError:
                os.kill(os.getpid(), signal.SIGINT)

            if subchoice == 'remove host':
                ctx.invoke(removehost) 

            elif subchoice == 'stop honeypot':
                ctx.invoke(stophoneypot) 

            elif subchoice == 'uninstall honeypot':
                ctx.invoke(uninstallhoneypot) 

        elif choice == 'exit':
            os.kill(os.getpid(), signal.SIGINT)


@main.command()
def addhost():
    """
    Add a host
    """

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
    ], style=style)

    hostname = new_host.pop("hostname")
    new_host["status"] = "inactive"
    new_host["installed"] = "False"
    host_value = str(new_host)
    config.set('HOSTS', hostname, host_value)
    writeConfig("New host " + hostname + " saved!")


@click.pass_context
def hostselector(ctx, message): 
    if len(config.items("HOSTS")) is 0:
        log("No hosts have been added yet. To add a host, select 'Add Host' command.", "red")
        ctx.invoke(choices)

    host_choices = [Separator('== Honeypots =='), ]

    for host in list(config['HOSTS']):
        host_choices.append({
            'name': host
        })

    return prompt([
        {
            'type': 'checkbox',
            'name': 'hosts',
            'message': message,
            'choices': host_choices
        }
    ], style=style)['hosts']

@main.command()
@click.pass_context
def removehost(ctx):
    """
    Remove a host
    """

    honeypots = hostselector("Which host(s) do you want to remove?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

        hosts = config.items('HOSTS')

        for host in hosts: 
            if host[0] in honeypots: 
                host_data = json.loads(host[1].replace("\'", "\""))
                installed = host_data['installed']

                if installed == "True": 
                    log(host[0] + " has a honeypot installed. To uninstall this honeypot, select 'Uninstall Honeypot' command.", "red")
                else: 
                    removed = config.remove_option('HOSTS', host[0])

                    if removed: 
                        log(host[0] + " has been removed.", "green")
                    else: 
                        log(host[0] + " could not be removed.", "red")
    


@main.command()
@click.pass_context
def starthoneypot(ctx):
    """
    Start a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to start a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

        tar_file = prompt([
            {
                'type': 'input',
                'name': 'tar_file',
                'message': 'Tar File:',
                'validate': FilePathValidator
            }
        ], style=style)['tar_file']

        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                status = host_data['status']

                if status == "active": 
                    log (host[0] + " is already running a honeypot.", "red")
                else: 
                    user = host_data['user']
                    ip = host_data['ip']
                    ssh_key = host_data['ssh_key']

                    password = prompt([
                        {
                            'type': 'password',
                            'name': 'password',
                            'message': ('Password for ' + user + "@" + ip + ":"),
                        }
                    ], style=style)['password']

                    stdout, stderr = subprocess.Popen(['deployment/deploy.sh', ssh_key, ip, user, password, tar_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()

                    print (("" + stdout.decode() + stderr.decode()))

                    # TODO: check for errors, do not label host as "active" if there were any errors with deployment
                    host_data['status'] = 'active'
                    host_data['installed'] = 'True'
                    host_value = str(host_data)
                    config.set('HOSTS', host[0], host_value)

                    log (host[0] + " is now running a honeypot.", "green")


@main.command()
def stophoneypot():
    """
    Stop a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to stop a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                status = host_data['status']

                if status == "inactive": 
                    log (host[0] + " was not running a honeypot.", "red")
                else: 
                    user = host_data['user']
                    ip = host_data['ip']
                    ssh_key = host_data['ssh_key']

                    password = prompt([
                        {
                            'type': 'password',
                            'name': 'password',
                            'message': ('Password for ' + user + "@" + ip + ":"),
                        }
                    ], style=style)['password']

                    # TODO: DELETE BEFORE PUTTING ON MASTER
                    print ("DEBUG VARIABLES (to be removed after tested)")
                    print ("============================================")

                    print ("KEYPATH: " + ssh_key)
                    print ("REMOTEIP: " + ip)
                    print ("REMOTENAME: " + user)
                    print ("REMOTEPASS: " + password)

                    # TODO: call the stop script
                    '''
                    stdout, stderr = subprocess.Popen(['deployment/deploy.sh', ssh_key, ip, user, password, tar_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()
                    

                    print (("" + stdout.decode() + stderr.decode()))
                    '''
                    print ("TODO - CALL A STOP SCRIPT WITH ABOVE VARIABLES")

                    # TODO: check for errors, do not label host as "inactive" if there were any errors with shutdown 
                    host_data['status'] = 'inactive'
                    host_value = str(host_data)
                    config.set('HOSTS', host[0], host_value)

                    log ("The honeypot on " + host[0] + " is now stopped.", "red")


@main.command()
def uninstallhoneypot():
    """
    Stop and uninstall a honeypot
    """

    honeypots = hostselector("Which host(s) do you want to uninstall a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                installed = host_data['installed']

                if installed == "False": 
                    log (host[0] + " did not have an installed honeypot.", "red")
                else: 
                    user = host_data['user']
                    ip = host_data['ip']
                    ssh_key = host_data['ssh_key']

                    password = prompt([
                        {
                            'type': 'password',
                            'name': 'password',
                            'message': ('Password for ' + user + "@" + ip + ":"),
                        }
                    ], style=style)['password']

                    # TODO: DELETE BEFORE PUTTING ON MASTER
                    print ("DEBUG VARIABLES (to be removed after tested)")
                    print ("============================================")

                    print ("KEYPATH: " + ssh_key)
                    print ("REMOTEIP: " + ip)
                    print ("REMOTENAME: " + user)
                    print ("REMOTEPASS: " + password)

                    # TODO: call the uninstall script
                    '''
                    stdout, stderr = subprocess.Popen(['deployment/deploy.sh', ssh_key, ip, user, password, tar_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()
                    

                    print (("" + stdout.decode() + stderr.decode()))
                    '''
                    print ("TODO - CALL AN UNINSTALL SCRIPT WITH ABOVE VARIABLES")

                    # TODO: check for errors, do not label host as uninstalled if there were any errors with uninstall 
                    host_data['status'] = 'inactive'
                    host_data['installed'] = 'False'
                    host_value = str(host_data)
                    config.set('HOSTS', host[0], host_value)

                    log ("The honeypot on " + host[0] + " is now uninstalled.", "green")


@main.command()
def reinstallhoneypot():
    """
    Reinstall and restart a honeypot 
    """

    honeypots = hostselector("Which host(s) do you want to reinstall a honeypot on?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

        tar_file = prompt([
            {
                'type': 'input',
                'name': 'tar_file',
                'message': 'Tar File:',
                'validate': FilePathValidator
            }
        ], style=style)['tar_file']

        hosts = config.items('HOSTS')

        for host in hosts:
            if host[0] in honeypots:
                host_data = json.loads(host[1].replace("\'", "\""))
                installed = host_data['installed']

                if installed == "False": 
                    # TODO: may not be necessary depending on reinstall script 
                    log (host[0] + " did not have an installed honeypot.", "red")
                else: 
                    user = host_data['user']
                    ip = host_data['ip']
                    ssh_key = host_data['ssh_key']

                    password = prompt([
                        {
                            'type': 'password',
                            'name': 'password',
                            'message': ('Password for ' + user + "@" + ip + ":"),
                        }
                    ], style=style)['password']

                    # TODO: DELETE BEFORE PUTTING ON MASTER
                    print ("DEBUG VARIABLES (to be removed after tested)")
                    print ("============================================")

                    print ("KEYPATH: " + ssh_key)
                    print ("REMOTEIP: " + ip)
                    print ("REMOTENAME: " + user)
                    print ("REMOTEPASS: " + password)
                    print ("REPOPATH: " + tar_file)

                    # TODO: call the reinstall script
                    '''
                    stdout, stderr = subprocess.Popen(['deployment/deploy.sh', ssh_key, ip, user, password, tar_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE).communicate()

                    print (("" + stdout.decode() + stderr.decode()))
                    '''

                    print ("TODO - CALL A REINSTALL SCRIPT WITH ABOVE VARIABLES")

                    # TODO: check for errors, do not label host as "active" if there were any errors with redeployment
                    host_data['status'] = 'active'
                    host_value = str(host_data)
                    config.set('HOSTS', host[0], host_value)

                    log ("The honeypot on " + host[0] + " is now reinstalled.", "green")


@main.command()
def configurehoneypot():
    """
    Configure a honeypot through a live ConfigTunnel connection 
    """

    honeypots = hostselector("Which host(s) do you want to configure?")

    if len(honeypots) == 0:
        log ("No host has been selected.", "red")
    else:

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
        ], style=style)['choice']

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
            ], style=style)['subchoice']

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
                        tunnel.send(message)
                        log ("Ran '" + message + "' on " + host[0], "green")

                    tunnel.stop()
                    tunnel.join()


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
    else:

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

if __name__ == '__main__':
    main()