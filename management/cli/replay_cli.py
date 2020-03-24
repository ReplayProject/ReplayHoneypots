
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


class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


"""
################
AND SO IT BEGINS
################
"""


@click.group()
@click.pass_context
def main(ctx):
    """
    Straightforward CLI for managing & deploying honeypots
    """
    ctx.ensure_object(dict)


class SSHKEYValidator(Validator):
    def validate(self, value):
        if len(value.text):
            print(value.text)
            output = os.popen('ssh-keygen -l -f ' + value.text)
            output.read()
            if output.close() is not None:
                raise ValidationError(
                    message="That is not a valid ssh key",
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


def askSSHKEY():
    """
    prompts user for their SSH Keyfile
    """
    questions = [
        {
            'type': 'input',
            'name': 'ssh_key',
            'message': 'Enter path to SSHKEY for use with remote hosts\n',
            'validate': SSHKEYValidator,
        },
    ]
    return prompt(questions, style=style).get("ssh_key")


@main.command()
@click.option('-i', '--identity', 'key_file', type=click.Path(exists=True, file_okay=True))
@click.pass_context
def checkstatus(ctx, key_file):
    """
    Check the status of devices
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



class DeviceIPValidator(Validator):
    """
    Validate an IP address based on ping response
    """
    def validate(self, value):

        if len(value.text):
            # TODO: verify valid ip format? 
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


@main.command()
def addhost():
    """
    Add a device
    """

    new_device = prompt([
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
            'name': 'port',
            'message': 'Port:',
            'validate': EmptyValidator
        }
    ], style=style)

    # TODO: ping on port
    
    hostname = new_device.pop("hostname")
    new_device["status"] = "inactive"
    host_value = str(new_device)
    config.set('HOSTS', hostname, host_value)
    writeConfig("New host " + hostname + " saved!")


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
            ctx.invoke(addhost)

        elif choice == 'remove host':
            # TODO
            ctx.invoke(choices)

        elif choice == 'start honeypot': 
            # TODO
            ctx.invoke(choices)

        elif choice == 'stop honeypot':
            # TODO
            ctx.invoke(choices)

        elif choice == 'check status':
            ctx.invoke(checkstatus)

        elif choice == 'open config':
            log("Opening Config file...", "green")
            subprocess.Popen(['nano', CONF_PATH]).wait()
            log("Reloading Edited Config file", "green")
            config = configparser.ConfigParser()
            setupConfig()

        elif choice == 'exit':
            os.kill(os.getpid(), signal.SIGINT)


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


if __name__ == '__main__':
    main()


# New Command Template
# @main.command()
# @click.argument('option')
# def test(debug, option=""):
#     pass
