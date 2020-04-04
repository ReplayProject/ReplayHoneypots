import subprocess
import os
import sys
import argparse

"""
This file generates restart.sh, which checks if PortThreadManager.py is running
and restarts it if not.

Additionally, this file edits the user's crontab file to run restart.sh based
on the given interval.
"""

class CronInstaller: 
    def main(main_args): 
        parser = argparse.ArgumentParser(description='Installs Crontab and restart.sh')
        parser.add_argument('-p', '--python', help='python file of the honeypot', required=True)
        parser.add_argument('-n', '--nmap', help='nmap file')
        args = parser.parse_args(main_args)

        if os.geteuid() != 0:
            print ("You must have root privileges to install Cron.")
            exit()

        script_file = ""
        with open(args.python, "r") as pythonFile: 
            script_file = pythonFile.name

        if args.nmap: 
            with open(args.nmap, "r") as nmapFile: 
                nmap_file = nmapFile.name
                CronInstaller.install(script_file, "-n", nmap_file)
        else: 
            CronInstaller.install(script_file)

    def install(script_file, mode="default", config_file="default"): 
        # Create the restart script
        restart_file = open("restart.sh", 'w')

        # Write the restart script using input
        script_file = os.path.abspath(script_file)
        config_file = os.path.abspath(config_file)
        restart_file.write("#!/bin/bash\n\n" +
                        "var=$(pgrep -af PortThreadManager.py | wc -l)\n\n" +
                        "if [ $var -le 0 ]\n" +
                        "then\n" +
                        "\techo $(date) 'Running: python3 " + script_file + " " + mode + " " + config_file + ".' >> " + os.path.dirname(os.path.dirname(script_file)) + "/logs/cron.txt\n" +
                        "\tcd " + os.path.dirname(os.path.dirname(script_file)) + " && pip3 install -r requirements.txt\n" +
                        "\tcd " + os.path.dirname(script_file) + " && python3 " + script_file + " " + mode + " " + config_file + "\n" +
                        "fi\n")

        restart_file.close()

        job = "* * * * * /bin/bash " + os.path.dirname(script_file) + \
            "/restart.sh >> " + os.path.dirname(os.path.dirname(script_file)) + "/logs/restart.txt 2>&1\n"

        # Check current crontab file (if it exists)
        process = subprocess.Popen(['crontab', '-l'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Create new crontab file
        crontab_file = open("honeypot", 'w')

        if "no crontab" in stderr.decode():  # If there is no previous crontab file:
            # Write the job into the new crontab file
            crontab_file.write(job)
            crontab_file.close()

            # Run crontab with the new crontab file
            process = subprocess.Popen(['crontab', 'honeypot'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
        else:
            if job in stdout.decode():
                crontab_file.close()
            else:  # If the previous crontab file doesn't contain our job:
                # Write the previous crontab file into the new crontab file
                crontab_file.write(stdout.decode())

                # Write the job into the new crontab file
                crontab_file.write(job)
                crontab_file.close()

                # Run crontab with the new crontab file
                process = subprocess.Popen(['crontab', 'honeypot'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

        # Remove generated files
        os.remove("honeypot")

if __name__ == '__main__':
    CronInstaller.main(sys.argv[1:])