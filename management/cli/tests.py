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
    Test adding a valid host when there are no hosts

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
    Test adding a host with the following invalid fields: 
    - using a hostname that already exists
    - using an IP address that already exists
    - using a folder for the ssh key insted of a file
    - using an invalid filepath for the ssh key

    Expected: 
    - user receives relevant error messae
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
        terminal.sendline('deployment/bad_file_name')
        terminal.expect('File deployment/bad_file_name could not be found')
        terminal.terminate()

    def test_remove_host_valid(self): 
        self.test_add_host_valid()
        terminal = pexpect.spawn('python3 replay_cli.py removehost --hosts yogi')
        terminal.expect('yogi has been removed.')


if __name__ == '__main__':
    unittest.main()