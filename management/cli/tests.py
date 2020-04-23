import unittest
import os
import subprocess
import pty
import pexpect
import sys

"""
Handles testing for the CLI
"""
class TestCLI(unittest.TestCase):


    """
    Clear any previous CLI configurations
    """
    def setUp(self): 
        try: 
            os.remove('honeycli.cfg')
        except OSError: 
            pass


    """
    Test host selector when there are no hosts

    Expected:
    - no host is found
    - no host is selected
    """
    def test_no_host(self): 
        terminal = pexpect.spawn('python3 replay_cli.py removehost')
        terminal.expect('No hosts have been added yet.')
        terminal.expect('No host has been selected.')
        terminal.terminate()
    

    """
    Test adding a valid host

    Expected: 
    - host is added
    """
    def test_add_host_valid(self): 
        terminal = pexpect.spawn('python3 replay_cli.py addhost')
        terminal.expect('Hostname:')
        terminal.sendline('yogi')
        terminal.expect('Username:')
        terminal.sendline('yogi')
        terminal.expect('IP Address:')
        terminal.sendline('192.168.23.52')
        terminal.expect('SSH Key:')
        terminal.sendline('deployment/manager_rsa')
        terminal.expect('New host yogi saved!')
        terminal.terminate()


    """
    Test removing a valid host

    Expected: 
    - host is removed
    """
    def test_remove_host_valid(self): 
        self.test_add_host_valid()
        terminal = pexpect.spawn('python3 replay_cli.py removehost --hosts yogi')
        terminal.expect('yogi has been removed.')
        terminal.terminate()


    """
    Test checking the status of a valid host

    Expected: 
    - status is output
    """
    def test_check_status_valid(self): 
        self.test_add_host_valid()
        terminal = pexpect.spawn('python3 replay_cli.py checkstatus --hosts yogi')
        terminal.expect('Linux yogi')
        terminal.terminate()


    """
    Test installing a honeypot on a valid host

    Expected: 
    - honeypot is installed
    """
    def test_install_honeypot_valid(self): 
        self.test_add_host_valid()
        terminal = pexpect.spawn('python3 replay_cli.py installhoneypot --hosts yogi')
        terminal.expect('Tar File:')
        terminal.sendline('deployment/repo.tar.gz')
        terminal.expect('yogi now has an installed honeypot.')
        terminal.terminate()


    """
    Test adding a host with the following invalid options: 
    - using a hostname that already exists
    - using an IP address that already exists
    - using a folder for the ssh key insted of a file
    - using an invalid filepath for the ssh key

    Expected: 
    - user receives relevant error message
    - host is not added
    """
    def test_add_host_invalid(self): 
        self.test_add_host_valid()
        terminal = pexpect.spawn('python3 replay_cli.py addhost')
        terminal.expect('Hostname:')
        terminal.sendline('yogi')
        terminal.expect('A host with that hostname already exists.')
        terminal.terminate()

        terminal = pexpect.spawn('python3 replay_cli.py addhost')
        terminal.expect('Hostname:')
        terminal.sendline('winnie')
        terminal.expect('Username:')
        terminal.sendline('winnie')
        terminal.expect('IP Address:')
        terminal.sendline('192.168.23.52')
        terminal.expect('A host with that IP address already exists.')
        terminal.terminate()

        terminal = pexpect.spawn('python3 replay_cli.py addhost')
        terminal.expect('Hostname:')
        terminal.sendline('winnie')
        terminal.expect('Username:')
        terminal.sendline('winnie')
        terminal.expect('IP Address:')
        terminal.sendline('192.168.23.51')
        terminal.expect('SSH Key:')
        terminal.sendline('deployment')
        terminal.expect('File deployment could not be found')
        terminal.terminate()

        terminal = pexpect.spawn('python3 replay_cli.py addhost')
        terminal.expect('Hostname:')
        terminal.sendline('winnie')
        terminal.expect('Username:')
        terminal.sendline('winnie')
        terminal.expect('IP Address:')
        terminal.sendline('192.168.23.51')
        terminal.expect('SSH Key:')
        terminal.sendline('deployment/bad_file_path')
        terminal.expect('File deployment/bad_file_path could not be found')
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
        terminal = pexpect.spawn('python3 replay_cli.py removehost --hosts unknown')
        terminal.expect('Host unknown could not be found.')
        terminal.terminate()

        self.test_install_honeypot_valid()
        terminal = pexpect.spawn('python3 replay_cli.py removehost --hosts yogi')
        terminal.expect('yogi has a honeypot installed.')
        terminal.terminate()


    """
    Test checking the status of a host with the following invalid options: 
    - using a hostname that doesn't exist

    NOT TESTED: 
    - valid but inaccessible host (e.g. no SSH, machine is shut down)

    Expected: 
    - user receives relevant error message
    - no status is output
    """
    def test_check_status_invalid(self): 
        terminal = pexpect.spawn('python3 replay_cli.py checkstatus --hosts unknown')
        terminal.expect('Host unknown could not be found.')
        terminal.terminate()


    """
    Test installing a honeypot with the following invalid options: 
    - using a hostname that doesn't exist
    - using a folder for the tar file insted of a file
    - using an invalid filepath for the tar file
    - using a host that already has a honeypot installed

    Expected: 
    - honeypot is installed
    """
    def test_install_honeypot_invalid(self): 
        terminal = pexpect.spawn('python3 replay_cli.py installhoneypot --hosts unknown')
        terminal.expect('Tar File:')
        terminal.sendline('deployment/repo.tar.gz')
        terminal.expect('Host unknown could not be found.')
        terminal.terminate()

        terminal = pexpect.spawn('python3 replay_cli.py installhoneypot --hosts yogi')
        terminal.expect('Tar File:')
        terminal.sendline('deployment')
        terminal.expect('File deployment could not be found')
        terminal.terminate()

        terminal = pexpect.spawn('python3 replay_cli.py installhoneypot --hosts yogi')
        terminal.expect('Tar File:')
        terminal.sendline('deployment/bad_file_path')
        terminal.expect('File deployment/bad_file_path could not be found')
        terminal.terminate()

        self.test_install_honeypot_valid()
        terminal = pexpect.spawn('python3 replay_cli.py installhoneypot --hosts yogi')
        terminal.expect('Tar File:')
        terminal.sendline('deployment/repo.tar.gz')
        terminal.expect('yogi already has an installed honeypot.')
        terminal.terminate()

        
if __name__ == '__main__':
    unittest.main()