import unittest
import os
import subprocess
import pty
import pexpect
import sys

hostname = "test"
user = "fakehoney"
password = "winniewazhere"
ip = "0.0.0.0"
ssh_port = "2222"
ssh_key = "test/privatekey"
db = "http://admin:couchdb@testingdb:25565"
tar_file = "deployment/repo.tar.gz"

"""
Handles testing for the CLI's managehosts submenu
"""


class TestManageHosts(unittest.TestCase):

    """
    Clear any previous CLI configurations
    """

    def setUp(self):
        # Confirm that the user has root access
        self.assertEqual(os.geteuid(), 0)

        try:
            os.remove("honeycli.cfg")
        except OSError:
            pass

    """
    Test host selector when there are no hosts

    Expected:
    - no host is found
    - no host is selected
    """

    def test_no_host(self):
        terminal = pexpect.spawn("python3 replay_cli.py removehost")
        terminal.expect("No hosts have been added yet.")
        terminal.expect("No host has been selected.")
        terminal.terminate()

    """
    Test adding a valid host

    Expected:
    - host is added
    """

    def test_add_host_valid(self):
        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline(hostname)
        terminal.expect("Username:")
        terminal.sendline(user)
        terminal.expect("IP Address:")
        terminal.sendline(ip)
        terminal.expect("Port:")
        terminal.sendline(ssh_port)
        terminal.expect("SSH Key:")
        terminal.sendline(ssh_key)
        terminal.expect("New host {} saved!".format(hostname))
        terminal.terminate()

    """
    Test removing a valid host

    Expected:
    - host is removed
    """

    def test_remove_host_valid(self):
        self.test_add_host_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py removehost --hosts {}".format(hostname)
        )
        terminal.expect("{} has been removed.".format(hostname))
        terminal.terminate()

    """
    Test checking the status of a valid host

    Expected:
    - status is output
    """

    def test_check_status_valid(self):
        self.test_add_host_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py checkstatus --hosts {}".format(hostname)
        )
        terminal.expect("Linux")
        terminal.terminate()

    """
    Test adding a host with the following invalid options:
    - using a hostname that already exists
    - using an IP address that already exists
    - using an invalid port number
    - using a folder for the ssh key instead of a file
    - using an invalid filepath for the ssh key

    NOT TESTED:
    - using an invalid username for a valid IP address
    - using a valid IP address for an inaccessible machine (e.g. no SSH, machine shut down)
    - using a valid filepath of an invalid ssh key file

    Expected:
    - user receives relevant error message
    - host is not added
    """

    def test_add_host_invalid(self):
        self.test_add_host_valid()
        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline(hostname)
        terminal.expect("A host with that hostname already exists.")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline(ip)
        terminal.expect("A host with that IP address already exists.")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline("notanint")
        terminal.expect("invalid literal for int")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline("6.9")
        terminal.expect("invalid literal for int")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline("-1")
        terminal.expect("Port must be between 0 and 65535")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline("65536")
        terminal.expect("Port must be between 0 and 65535")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline(ssh_port)
        terminal.expect("SSH Key:")
        terminal.sendline("test")
        terminal.expect("File test could not be found")
        terminal.terminate()

        terminal = pexpect.spawn("python3 replay_cli.py addhost")
        terminal.expect("Hostname:")
        terminal.sendline("newhostname")
        terminal.expect("Username:")
        terminal.sendline("newuser")
        terminal.expect("IP Address:")
        terminal.sendline("127.0.0.1")
        terminal.expect("Port:")
        terminal.sendline(ssh_port)
        terminal.expect("SSH Key:")
        terminal.sendline("test/bad_file_path")
        terminal.expect("File test/bad_file_path could not be found")
        terminal.terminate()

    """
    Test removing a host with the following invalid options:
    - using a hostname that doesn't exist
    - using a host that has a honeypot installed

    Expected:
    - user receives relevant error message
    - host is not removed
    """

    def test_remove_host_invalid(self):
        terminal = pexpect.spawn("python3 replay_cli.py removehost --hosts unknown")
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        TestInstall.test_install_honeypot_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py removehost --hosts {}".format(hostname)
        )
        terminal.expect("{} has a honeypot installed.".format(hostname))
        terminal.terminate()

    """
    Test checking the status of a host with the following invalid options:
    - using a hostname that doesn't exist

    Expected:
    - user receives relevant error message
    - no status is output
    """

    def test_check_status_invalid(self):
        terminal = pexpect.spawn("python3 replay_cli.py checkstatus --hosts unknown")
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()


"""
Handles testing for the CLI's install submenu
"""


class TestInstall(unittest.TestCase):

    """
    Clear any previous CLI configurations
    """

    def setUp(self):
        # Confirm that the user has root access
        self.assertEqual(os.geteuid(), 0)

        try:
            os.remove("honeycli.cfg")
        except OSError:
            pass

    """
    Test installing a honeypot on a valid host

    Expected:
    - honeypot is installed
    """

    def test_install_honeypot_valid(self):
        TestManageHosts.test_add_host_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py installhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("{} now has an installed honeypot.".format(hostname))
        terminal.terminate()

    """
    Test uninstalling a honeypot on a valid host

    Expected:
    - honeypot is uninstalled
    """

    def test_uninstall_honeypot_valid(self):
        self.test_install_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py uninstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline(password)
        terminal.expect("The honeypot on {} is now uninstalled.".format(hostname))
        terminal.terminate()

    """
    Test reinstalling a honeypot on a valid host

    Expected:
    - honeypot is reinstalled
    """

    def test_reinstall_honeypot_valid(self):
        self.test_install_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py reinstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline(password)
        terminal.expect("The honeypot on {} is now reinstalled.".format(hostname))
        terminal.terminate()

    """
    Test installing a honeypot with the following invalid options:
    - using a hostname that doesn't exist
    - using a folder for the tar file instead of a file
    - using an invalid filepath for the tar file
    - using a host that already has a honeypot installed

    NOT TESTED:
    - using a valid filepath of an invalid tar file

    Expected:
    - honeypot is not installed
    """

    def test_install_honeypot_invalid(self):
        terminal = pexpect.spawn(
            "python3 replay_cli.py installhoneypot --hosts unknown"
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        terminal = pexpect.spawn(
            "python3 replay_cli.py installhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline("test")
        terminal.expect("File test could not be found")
        terminal.terminate()

        terminal = pexpect.spawn(
            "python3 replay_cli.py installhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline("test/bad_file_path")
        terminal.expect("File test/bad_file_path could not be found")
        terminal.terminate()

        self.test_install_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py installhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("{} already has an installed honeypot.".format(hostname))
        terminal.terminate()

    """
    Test uninstalling a honeypot with the following invalid options:
    - using a hostname that doesn't exist
    - using a host that didn't have a honeypot installed
    - using an invalid password

    Expected:
    - honeypot is not uninstalled
    """

    def test_uninstall_honeypot_invalid(self):
        terminal = pexpect.spawn(
            "python3 replay_cli.py uninstallhoneypot --hosts unknown"
        )
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        self.test_uninstall_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py uninstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("{} did not have an installed honeypot.".format(hostname))
        terminal.terminate()

        self.setUp()
        self.test_install_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py uninstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline("badpass")
        terminal.expect("The honeypot on {} failed to uninstall.".format(hostname))
        terminal.terminate()

    """
    Test reinstalling a honeypot with the following invalid options:
    - using a hostname that doesn't exist
    - using a folder for the tar file instead of a file
    - using an invalid filepath for the tar file
    - using a host that didn't have a honeypot installed

    NOT TESTED:
    - using a valid filepath of an invalid tar file
    - using an invalid password (reinstall.sh doesn't seem to trap/catch that error)

    Expected:
    - honeypot is not reinstalled
    """

    def test_reinstall_honeypot_invalid(self):
        terminal = pexpect.spawn(
            "python3 replay_cli.py reinstallhoneypot --hosts unknown"
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        terminal = pexpect.spawn(
            "python3 replay_cli.py reinstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline("test")
        terminal.expect("File test could not be found")
        terminal.terminate()

        terminal = pexpect.spawn(
            "python3 replay_cli.py reinstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline("test/bad_file_path")
        terminal.expect("File test/bad_file_path could not be found")
        terminal.terminate()

        self.test_uninstall_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py reinstallhoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Tar File:")
        terminal.sendline(tar_file)
        terminal.expect("{} did not have an installed honeypot.".format(hostname))
        terminal.terminate()


"""
Handles testing for the CLI's edithoneypots submenu
"""


class TestEditHoneypots(unittest.TestCase):

    """
    Clear any previous CLI configurations
    """

    def setUp(self):
        # Confirm that the user has root access
        self.assertEqual(os.geteuid(), 0)

        try:
            os.remove("honeycli.cfg")
        except OSError:
            pass

    """
    Test starting a honeypot on a valid host

    Expected:
    - honeypot is started
    """

    def test_start_honeypot_valid(self):
        TestInstall.test_install_honeypot_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py starthoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Database URL:")
        terminal.sendline(db)
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline(password)
        terminal.expect("{} is now running a honeypot.".format(hostname))
        terminal.terminate()

    """
    Test stopping a honeypot on a valid host

    Expected:
    - honeypot is stopped
    """

    def test_stop_honeypot_valid(self):
        self.test_start_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py stophoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline(password)
        terminal.expect("The honeypot on {} is now stopped.".format(hostname))
        terminal.terminate()

    """
    Test starting a honeypot with the following invalid options:
    - using a hostname that doesn't exist
    - using a host that didn't have a honeypot installed
    - using a host that was already started
    - using an invalid password

    NOT TESTED:
    - using a valid string of an invalid database url

    Expected:
    - honeypot is not started
    """

    def test_start_honeypot_invalid(self):
        terminal = pexpect.spawn("python3 replay_cli.py starthoneypot --hosts unknown")
        terminal.expect("Database URL:")
        terminal.sendline(db)
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        TestManageHosts.test_add_host_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py starthoneypot --hosts {}".format(hostname)
        )
        terminal.expect("{} did not have an installed honeypot.".format(hostname))
        terminal.terminate()

        self.setUp()
        self.test_start_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py starthoneypot --hosts {}".format(hostname)
        )
        terminal.expect("{} is already running a honeypot.".format(hostname))
        terminal.terminate()

        self.setUp()
        TestInstall.test_install_honeypot_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py starthoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Database URL:")
        terminal.sendline(db)
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline("badpass")
        terminal.expect("{} failed to start a honeypot.".format(hostname))
        terminal.terminate()

    """
    Test stopping a honeypot with the following invalid options:
    - using a hostname that doesn't exist
    - using a host that didn't have a honeypot installed
    - using a host that was already stopped
    - using an invalid password

    Expected:
    - honeypot is not stopped
    """

    def test_stop_honeypot_invalid(self):
        terminal = pexpect.spawn("python3 replay_cli.py stophoneypot --hosts unknown")
        terminal.expect("Host unknown could not be found.")
        terminal.terminate()

        TestManageHosts.test_add_host_valid(self)
        terminal = pexpect.spawn(
            "python3 replay_cli.py stophoneypot --hosts {}".format(hostname)
        )
        terminal.expect("{} did not have an installed honeypot.".format(hostname))
        terminal.terminate()

        self.setUp()
        self.test_stop_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py stophoneypot --hosts {}".format(hostname)
        )
        terminal.expect("{} was not running a honeypot.".format(hostname))
        terminal.terminate()

        self.setUp()
        self.test_start_honeypot_valid()
        terminal = pexpect.spawn(
            "python3 replay_cli.py stophoneypot --hosts {}".format(hostname)
        )
        terminal.expect("Password for {}@{}:".format(user, ip))
        terminal.sendline("badpass")
        terminal.expect("The honeypot on {} failed to stop.".format(hostname))
        terminal.terminate()


if __name__ == "__main__":
    unittest.main()
