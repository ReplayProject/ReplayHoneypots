import os
import six
import json
import click
import ipaddress
import configparser
from pyfiglet import figlet_format
from PyInquirer import (
    Token,
    style_from_dict,
    Separator,
    prompt,
    ValidationError,
    Validator,
)


"""
#######
Visuals
#######
"""


try:
    import colorama

    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(string, font=font), color))
    else:
        six.print_(string)


"""
#############
Interactivity
#############
"""


def style():
    return style_from_dict(
        {
            Token.QuestionMark: "#fac731 bold",
            Token.Answer: "#4688f1 bold",
            Token.Instruction: "",  # default
            Token.Separator: "#cc5454",
            Token.Selected: "#0abf5b",  # default
            Token.Pointer: "#673ab7 bold",
            Token.Question: "",
        }
    )


@click.pass_context
def hostselector(ctx, message):
    if len(config.items("HOSTS")) == 0:
        log(
            (
                "No hosts have been added yet."
                "To add a host, select 'Add/Update Host > Add Host' command."
            ),
            "red",
        )
        return []

    host_choices = [
        Separator("== Honeypots =="),
    ]

    for host in list(config["HOSTS"]):
        host_choices.append({"name": host})

    try:
        return prompt(
            [
                {
                    "type": "checkbox",
                    "name": "hosts",
                    "message": message,
                    "choices": host_choices,
                }
            ],
            style=style(),
        )["hosts"]
    except EOFError:
        log("Action cancelled by user", "red")
        return []


"""
#############
Configuration
#############
"""

CONF_PATH = "honeycli.cfg"
config = configparser.ConfigParser()


def setupConfig():
    try:
        with open(CONF_PATH) as f:
            config.read_file(f)
    except IOError:
        pass

    if not config.has_section("HOSTS"):
        config.add_section("HOSTS")
    if not config.has_section("GENERAL"):
        config.add_section("GENERAL")

    return config


def writeConfig(message):
    with open(CONF_PATH, "w") as f:
        config.write(f)
    log(message, "green")


def hosts():
    all_hosts = config.items("HOSTS")
    all_hostnames = []

    for host in all_hosts:
        all_hostnames.append(host[0])

    return all_hostnames


def hostdata(hostname):
    host = config.get("HOSTS", hostname)
    return json.loads(host.replace("'", '"'))


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
                ipaddress.ip_address(value.text)
            except ValueError as e:
                raise ValidationError(message=str(e), cursor_position=len(value.text))

            hosts = config.items("HOSTS")
            ip = []

            for host in hosts:
                data = json.loads(host[1].replace("'", '"'))
                ip.append(data["ip"])

            if value.text in ip:
                raise ValidationError(
                    message=(
                        "A host with that IP address already exists. "
                        "To replace it, please remove host first."
                    ),
                    cursor_position=len(value.text),
                )
        else:
            raise ValidationError(
                message="You can't leave this blank", cursor_position=len(value.text)
            )


class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank", cursor_position=len(value.text)
            )


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
                    cursor_position=len(value.text),
                )
        else:
            raise ValidationError(
                message="You can't leave this blank", cursor_position=len(value.text)
            )


"""
Validate a hostname based on whether the hostname already exists in the CLI data
"""


class HostnameValidator(Validator):
    """
    Validate a hostname
    """

    def validate(self, value):

        if len(value.text):
            hosts = config.items("HOSTS")
            hostnames = []

            for host in hosts:
                hostnames.append(host[0])

            if value.text in hostnames:
                raise ValidationError(
                    message=(
                        "A host with that hostname already exists. "
                        "To replace it, please remove host first."
                    ),
                    cursor_position=len(value.text),
                )

        else:
            raise ValidationError(
                message="You can't leave this blank", cursor_position=len(value.text)
            )


class PortValidator(Validator):
    def validate(self, value):
        if len(value.text):
            try:
                port = int(value.text)

                if port < 0 or port > 65535:
                    raise ValidationError(
                        message="Port must be between 0 and 65535",
                        cursor_position=len(value.text),
                    )
            except ValueError as e:
                raise ValidationError(message=str(e), cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank", cursor_position=len(value.text)
            )
