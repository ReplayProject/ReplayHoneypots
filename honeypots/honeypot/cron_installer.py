import subprocess
import os

# Obtain the absolute path of the current directory and generate crontab job 
process = subprocess.Popen(['pwd'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

job = "*/10 * * * * /bin/bash " + stdout.replace("\n", "") + "/check.sh\n"

# Check current crontab file (if it exists)
process = subprocess.Popen(['crontab', '-l'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# Create new crontab file 
crontab_file = open("honeypot", 'w')

if "no crontab" in stderr: # If there is no previous crontab file: 
    # Write the job into the new crontab file
    crontab_file.write(job)
    crontab_file.close()

    # Run crontab with the new crontab file 
    process = subprocess.Popen(['crontab', 'honeypot'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
else: 
    if job in stdout: 
        crontab_file.close()
    else: # If the previous crontab file doesn't contain our job: 
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
