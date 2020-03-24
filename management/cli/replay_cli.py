
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
import itertools
import subprocess
import json
import ipaddress

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
Validators
"""


class DeviceIPValidator(Validator):
    """
    Validate an IP address based on ping response
    """
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
CLI Commands
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
            answers = prompt([
                {
                    'type': 'list',
                    'name': 'choice',
                    'message': 'What do you need to do?',
                    'choices':
                    ['Add Host',
                     'Remove Host',
                     'Start Honeypot',
                     'Stop Honeypot', 
                     'Check Status',
                     'Open Config',
                     'Exit'],
                    'filter': lambda val: val.lower()
                }
            ], style=style)

            choice = answers['choice']
        except KeyError:
            os.kill(os.getpid(), signal.SIGINT)

        if choice == 'add host':
            ctx.invoke(addhost) #done

        elif choice == 'remove host':
            ctx.invoke(removehost) #not started

        elif choice == 'start honeypot': 
            ctx.invoke(starthoneypot) #not started

        elif choice == 'stop honeypot':
            ctx.invoke(stophoneypot) #not started

        elif choice == 'check status':
            ctx.invoke(checkstatus) #wip 

        elif choice == 'open config': #wip
            log("Opening Config file...", "green")
            subprocess.Popen(['nano', CONF_PATH]).wait()
            log("Reloading Edited Config file", "green")
            config = configparser.ConfigParser()
            setupConfig()

        elif choice == 'exit': #done
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
            'message': 'SSH Key Absolute Path:',
            'validate': FilePathValidator,
        },
    ], style=style)

    hostname = new_host.pop("hostname")
    new_host["status"] = "inactive"
    host_value = str(new_host)
    config.set('HOSTS', hostname, host_value)
    writeConfig("New host " + hostname + " saved!")


@main.command()
def removehost():
    """
    Remove a host
    """

    # TODO
    log("TODO", "red")


@main.command()
@click.pass_context
def starthoneypot(ctx):
    """
    Start a honeypot
    """

    if len(config.items("HOSTS")) is 0:
        log("No hosts have been added yet. To add a host, select 'Add Host' command.", "red")
        ctx.invoke(choices)

    host_choices = [Separator('== Honeypots =='), ]

    for host in list(config['HOSTS']):
        host_choices.append({
            'name': host
        })

    answers = prompt([
        {
            'type': 'checkbox',
            'name': 'hosts',
            'message': 'Which host(s) do you want to start a honeypot on?',
            'choices': host_choices
        }
    ], style=style)

    honeypots = answers['hosts']

    if len(honeypots) == 0: 
        log ("No host has been selected.", "red")
    else: 
        hosts = config.items('HOSTS')
        
        for host in hosts: 
            if host[0] in honeypots: 
                host_data = json.loads(host[1].replace("\'", "\""))
                user = host_data['user']
                ip = host_data['ip']
                ssh_key = host_data['ssh_key']
                
                answers = prompt([
                    {
                        'type': 'password',
                        'name': 'pass',
                        'message': ('Password for ' + user + "@" + ip + ":"),
                    }
                ], style=style)
                
                # THIS WILL BE THE CALL TO BASH SCRIPTS - DELETE THESE PRINTS LATER
                print ("KEYPATH: " + ssh_key)
                print ("REMOTEIP: " + ip)
                print ("REMOTENAME: " + user)
                print ("REMOTEPASS: " + answers['pass'])

                host_data['status'] = 'active'
                host_value = str(host_data)
                config.set('HOSTS', host[0], host_value)


@main.command()
def stophoneypot():
    """
    Stop a honeypot
    """

    # TODO
    log("TODO", "red")


def askSSHKEY():
    """
    prompts user for their SSH Keyfile
    """
    questions = [
        {
            'type': 'input',
            'name': 'ssh_key',
            'message': 'Enter path to SSHKEY for use with remote hosts',
            'validate': FilePathValidator,
        },
    ]
    return prompt(questions, style=style).get("ssh_key")


@main.command()
@click.option('-i', '--identity', 'key_file', type=click.Path(exists=True, file_okay=True))
@click.pass_context
def checkstatus(ctx, key_file):
    """
    Check the status of hosts
    """

    if len(config.items("HOSTS")) is 0:
        log("No hosts have been added yet. To add a host, select 'Add Host' command.", "red")
        ctx.invoke(choices)

    ssh_key = None
    if config.has_option("GENERAL", "ssh_key"):
        ssh_key = conf.get("ssh_key")
    else:
        if key_file is not None:

            # TODO: figure out manual validation
            # SSHKEYValidator().validate({text:key_file})

            conf["ssh_key"] = ssh_key
            ssh_key = conf.get("ssh_key")
        else:
            ssh_key = askSSHKEY()
            if ssh_key is None:
                os.kill(os.getpid(), signal.SIGINT)
            conf["ssh_key"] = ssh_key
        writeConfig("SSHKEY Saved")

    host_choices = [Separator('== Honeypots =='), ]

    for x in list(config['HOSTS']):
        host_choices.append({
            'name': x + ' - ' + config['HOSTS'][x]
        })

    answers = prompt([
        {
            'type': 'checkbox',
            # 'qmark': '😃',
            'message': 'Which Devices do you want to check on?',
            'name': 'devices',
            'choices': host_choices,
            'validate': lambda answer: 'You must choose at least one host.'
            if len(answer) == 0 else False
        }
    ], style=style)

    # TODO: pick at least 1 not currently working
    print('\n\n')
    for device in answers['devices']:
        half = device.split('-')

        log("==== Output for " + half[0] + "====", "green")
        info = half[1].rstrip().split(':')

        cmd = 'ssh' + info[0] + "@" + info[1] + \
            " -p " + info[2] + ' "uname -a"'

        # TODO: attach to debug mode
        # log(cmd, "red")

        output = os.popen(cmd)
        pprint(output.read())
        print('\n\n')
        output.close()

    log("Work In Progress", color="blue")


if __name__ == '__main__':
    main()


# New Command Template
# @main.command()
# @click.argument('option')
# def test(debug, option=""):
#     pass
