import subprocess
import os
import sys

"""
This file generates restart.sh, which checks if PortThreadManager.py is running
and restarts it if not.

Additionally, this file edits the user's crontab file to run restart.sh based
on the given interval.
"""

# The usage message displayed for incorrect command line arguments
usage = ("usage: CronInstaller.py PortThreadManager.py [-c CONFIG] [-n NMAP]\n\n" +
        "optional arguments:\n" +
        "\t-c CONFIG\n" + 
        "\t\tconfig file\n" +
        "\t-n NMAP\n" + 
        "\t\tnmap file\n")

# Parse through the command line arguments 
if len(sys.argv) != 4:
    print (usage)
    exit()

script_file = os.path.abspath(sys.argv[1])
mode = sys.argv[2]
config_file = os.path.abspath(sys.argv[3])

if not os.path.exists(script_file) or (mode != "-c" and mode != "-n") or not os.path.exists(config_file):
    print (usage)
    exit()

# Create the restart script
restart_file = open("restart.sh", 'w')

# Write the restart script using input
restart_file.write("#!/bin/bash\n\n" +
                   "var=$(pgrep -af PortThreadManager.py | wc -l)\n\n" +
                   "if [ $var -gt 0 ]\n" +
                   "then\n" +
                   "\techo $(date) 'PortThreadManager.py is running.' >> " + os.path.dirname(os.path.dirname(script_file)) + "/logs/cron.txt\n" +
                   "else\n" +
                   "\techo $(date) 'Running: python3 " + script_file + " " + mode + " " + config_file + ".' >> " + os.path.dirname(os.path.dirname(script_file)) + "/logs/cron.txt\n" +
                   "\tcd " + os.path.dirname(os.path.dirname(script_file)) + " && pip3 install -r requirements.txt\n" +
                   "\tcd " + os.path.dirname(script_file) + " && python3 " + script_file + " " + mode + " " + config_file + "\n" +
                   "fi\n")

# Obtain the absolute path of the current directory and generate crontab job
process = subprocess.Popen(['pwd'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

job = "* * * * * /bin/bash " + stdout.decode().replace("\n", "") + \
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

