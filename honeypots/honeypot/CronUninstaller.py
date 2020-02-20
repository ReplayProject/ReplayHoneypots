import subprocess
import os

"""
This file edits the user's crontab file to stop running restart.sh.

Additionally, this file kills any remaining processes of PortThreadManager.py.

This file should be run by the same user who initially ran PortThreadManager.py.
"""

# Obtain the absolute path of the current directory and generate crontab job
process = subprocess.Popen(['pwd'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

job = stdout.decode().replace("\n", "") + "/restart.sh"

# Check current crontab file (if it exists)
process = subprocess.Popen(['crontab', '-l'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if "no crontab" in stderr.decode():  # If there is no previous crontab file:
    # Send an error message to the user
    print("No crontab file for this user.\n" +
          "CronUninstaller.py should be run by the same user who ran PortThreadManager.py.")
else:
    if job in stdout.decode():
        # Create new crontab file
        crontab_file = open("no_honeypot", 'w')

        # Write the previous crontab file into the new crontab file
        for line in stdout.decode().split("\n"):
            # Exclude restart.sh's job
            if not job in line:
                crontab_file.write(line + "\n")

        crontab_file.close()

        # Run crontab with the new crontab file
        process = subprocess.Popen(['crontab', 'no_honeypot'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Remove generated files
        os.remove("no_honeypot")

        # Check for any remaining processes of PortThreadManager.py
        process = subprocess.Popen(['pgrep', '-af', 'PortThreadManager.py'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        while stdout:  # While there are remaining processes of PortThreadManager.py:
            # Obtain first process
            process_details = stdout.decode().split("\n")[0]
            pid = process_details.split(" ")[0]

            # Kill first process
            process = subprocess.Popen(['kill', '-9', pid],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print("Killed process " + process_details)

            # Check for any remaining processes of PortThreadManager.py
            process = subprocess.Popen(['pgrep', '-af', 'PortThreadManager.py'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
    else:  # If the previous crontab file doesn't contain our job:
        # Send an error message to the user
        print("Crontab file does not contain " + job + ".\n" +
              "CronUninstaller.py should be run after PortThreadManager.py has been run.")
