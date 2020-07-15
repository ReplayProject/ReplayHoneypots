"""
This file generates restart.sh, which checks if PortThreadManager.py is running
and restarts it if not.

Additionally, this file edits the user's crontab file to run restart.sh based
on the given interval.

TODO: More direct and useful testing for this file needed.
"""
import argparse
import os
import subprocess
import sys


class CronInstaller:
    def main(self, main_args):
        parser = argparse.ArgumentParser(description="Installs Crontab and restart.sh")
        parser.add_argument(
            "-p", "--python", help="python file of the honeypot", required=True
        )
        parser.add_argument("-n", "--nmap", help="nmap file")
        parser.add_argument("-d", "--database", help="database url")
        args = parser.parse_args(main_args)

        if os.geteuid() != 0:
            print("You must have root privileges to install Cron.")
            exit()

        script_file = ""
        with open(args.python, "r") as pythonFile:
            script_file = pythonFile.name

        args_mode = ""
        args_config_file = ""
        if args.nmap:
            with open(args.nmap, "r") as nmapFile:
                args_mode = "-n"
                args_config_file = nmapFile.name

        args_database = ""
        if args.database:
            args_database = args.database

        CronInstaller.install(
            script_file,
            mode=args_mode,
            config_file=args_config_file,
            database=args_database,
        )

    def install(self, script_file, mode="", config_file="", database=""):
        # Create the restart script
        restart_file = open("restart.sh", "w")

        # Write the restart script using input
        script_file = os.path.abspath(script_file)
        config_file = os.path.abspath(config_file)

        restart_text = (
            "#!/bin/bash\n\n"
            + "var=$(pgrep -af PortThreadManager.py | wc -l)\n\n"
            + "if [ $var -le 0 ]\n"
            + "then\n"
            + "\tcd "
            + os.path.dirname(os.path.dirname(script_file))
            + " && pip3 install -r requirements.txt\n"
            + "\techo $(date) 'Running: sudo "
        )

        if database != "":
            restart_text += 'DB_URL="' + database + '" '

        restart_text += "python3 " + script_file

        if mode != "":
            restart_text += " " + mode + " " + config_file

        restart_text += (
            ".' >> "
            + os.path.dirname(os.path.dirname(os.path.dirname(script_file)))
            + "/logs/logs/cron.txt\n"
            + "\tcd "
            + os.path.dirname(script_file)
            + " && sudo "
        )

        if database != "":
            restart_text += 'DB_URL="' + database + '" '

        restart_text += "python3 " + script_file

        if mode != "":
            restart_text += " " + mode + " " + config_file

        restart_text += "\nfi\n"

        restart_file.write(restart_text)
        restart_file.close()

        job = (
            "* * * * * /bin/bash "
            + os.path.dirname(script_file)
            + "/restart.sh >> "
            + os.path.dirname(os.path.dirname(os.path.dirname(script_file)))
            + "/logs/logs/restart.txt 2>&1\n"
        )

        # Check current crontab file (if it exists)
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # Create new crontab file
        crontab_file = open("honeypot", "w")

        if "no crontab" in stderr.decode():  # If there is no previous crontab file:
            # Write the job into the new crontab file
            crontab_file.write(job)
            crontab_file.close()

            # Run crontab with the new crontab file
            process = subprocess.Popen(
                ["crontab", "honeypot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
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
                process = subprocess.Popen(
                    ["crontab", "honeypot"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()

        # Remove generated files
        os.remove("honeypot")


if __name__ == "__main__":
    CronInstaller.main(sys.argv[1:])
