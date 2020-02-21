import subprocess
import os

"""
This file generates restart.sh, which checks if PortThreadManager.py is running
and restarts it if not.

Additionally, this file edits the user's crontab file to run restart.sh based
on the given interval.
"""


class CronInstaller:
    def install(script_file, mode, config_file):
        # Create the restart script
        restart_file = open("restart.sh", 'w')

        # Write the restart script using input
        restart_file.write("#!/bin/bash\n\n" +
                           "var=$(pgrep -af python | grep PortThreadManager.py | wc -l)\n\n" +
                           "if [ $var -gt 0 ]\n" +
                           "then\n" +
                           "\techo $(date) 'PortThreadManager.py is running.' >> /home/winnie/check.log\n" +
                           "else\n" +
                           "\techo $(date) 'Running: python3 " + script_file + " " + mode + " " + config_file + ".' >> /home/winnie/check.log\n" +
                           "\tcd " + os.path.dirname(os.path.dirname(script_file)) + " && pip3 install -r requirements.txt\n" +
                           "\tcd " + os.path.dirname(script_file) + " && python3 " + script_file + " " + mode + " " + config_file + "\n" +
                           "fi")
        # Obtain the absolute path of the current directory and generate crontab job
        process = subprocess.Popen(['pwd'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        job = "* * * * * /bin/bash " + stdout.decode().replace("\n", "") + \
            "/restart.sh >> /home/winnie/out.log 2>&1\n"

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
                crontab_file.write(stdout)

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
