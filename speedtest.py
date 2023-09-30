import os
import re
import subprocess
import time


# SETTINGS:

# Define the IPv4 to connect to during the Iperf3 Network test and the Server ID to connect to during Speedtest.
# The Server ID can be found by typing "speedtest -L"

iperf = False       # Options: True/False ; Set to True if you are able to install an IPerf3 Host on your Firewall
target_ip = None    # Options: "123.123.123.123" / None ; Set the IPv4 Adress of your Firewall at which the IPerf3 Host is waiting for connections
target_id = None    # Options: "12345" / None ; Set the Server ID of a specific Ookla Speedtest Server if you wish to keep the Speedtest Results consistent


# Function to extract a value from a string using a regex pattern and set to "N/A" if not found
def extract_value(pattern, text):
    match = re.search(pattern, text)
    return match.group(1) if match else "N/A"

# Function to write .csv Files
def write_csvfile(filetype, field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_10):
    date = time.strftime('%d/%m/%y')
    timestamp = time.strftime('%H:%M')
    timestamp_log = time.strftime('%H:%M:%S')

    if filetype == "LOG":
        filename = os.path.join(logs_dir, 'isp-buster_logs.csv')
        fileheader = 'Date,Time,Log Type,Log Description,Log Output\r\n'
        fileformat = '{},{},{},{},{}\r\n'.format(date, timestamp_log, field_1, field_2, field_3)
    elif filetype == "TMPLOG":
        filename = os.path.join(tmp_logs_dir, 'isp-buster_tmplogs.csv')
        fileheader = 'Date,Time,Log Type,Log Description,Log Output\r\n'
        fileformat = '{},{},{},{},{}\r\n'.format(date, timestamp_log, field_1, field_2, field_3)
    elif filetype == "IPERF":
        filename = os.path.join(results_dir, 'isp-buster_iperf.csv')
        fileheader = 'Date,Time,Local (IPv4),Target (IPv4),Interval (sec),Transfer (MBytes),Bitrate (Mbits/sec),Retries\r\n'
        fileformat = '{},{},{},{},{},{},{},{}\r\n'.format(date, timestamp, field_1, field_2, field_3, field_4, field_5, field_6)
    elif filetype == "SPEEDTEST":
        filename = os.path.join(results_dir, 'isp-buster_speedtest.csv')
        fileheader = 'Date,Time,Server ID,Ping (ms),Jitter (ms),Download (Mbits/sec),Upload (Mbits/sec)\r\n'
        fileformat = '{},{},{},{},{},{}\r\n'.format(date, timestamp, field_1, field_2, field_3, field_4, field_5)
    elif filetype == "COMBINED":
        filename = os.path.join(results_dir, 'isp-buster_combined.csv')
        fileheader = 'Date,Time,IPerf Local (IPv4),IPerf Target (IPv4),IPerf Transfer (MBytes),IPerf Bitrate (Mbits/sec),IPerf Retries,Speedtest Server ID,Speedtest Ping (ms),Speedtest Jitter (ms),Speedtest Download (Mbits/sec),Speedtest Upload (Mbits/sec)\r\n'
        fileformat = '{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(date, timestamp, field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_10)

    try:
        logtype = "INFO"
        logoutput = ""
        logdescription = f"Successfully wrote to {filename}"

        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                f.write(fileheader)
        with open(filename, 'a+') as f:
            f.write(fileformat)

        print(logdescription)
        return 0, logtype, logdescription, logoutput
    except Exception as e:
        logtype = "ERROR"
        logoutput = e
        logdescription = f"An Error occurred while writing to {filename}"

        print(f"{logdescription}:")
        print(logoutput)
        return 1, logtype, logdescription, logoutput

# Initialize Filetype Variables for writing .csv Files
filetype_log = "LOG"
filetype_tmplog = "TMPLOG"
filetype_iperf = "IPERF"
filetype_speedtest = "SPEEDTEST"
filetype_combined = "COMBINED"

# Initialize Temporary Logfile Directory for when the Program is run without sudo and can't write a Logfile into /etc/isp-buster
user = os.getlogin()
tmp_logs_dir = f'/home/{user}'

try:
    # Create the results directory if it doesn't exist
    results_dir = '/etc/isp-buster/results'
    os.makedirs(results_dir, exist_ok=True)
    # Create the logs directory if it doesn't exist
    logs_dir = '/etc/isp-buster/logs'
    os.makedirs(results_dir, exist_ok=True)
except Exception as e:
    logtype = "ERROR"
    logoutput = e
    logdescription = "An Error occurred while creating the needed directories"

    print(f"{logdescription}:")
    print(logoutput)

    returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    if returncode[0] == 1:
        write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")


# Run the IPerf Test and log it into a .csv File if specified in the Settings
if iperf and target_ip != None:
    try:
        # Run the IPerf test
        iperf_output = subprocess.Popen(f'/usr/bin/iperf3 -c {target_ip}', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    except Exception as e:
        logtype = "ERROR"
        logoutput = e
        logdescription = "An Error occurred while running the IPerf3 Network Speedtest"
        iperf_output = ""

        print(f"{logdescription}:")
        print(logoutput)

        returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

        if returncode[0] == 1:
            write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    # Split the IPerf output into lines
    iperf_lines = iperf_output.splitlines()

    # Initialize variables to store the extracted data
    local_ip = "N/A"
    target_ip = "N/A"
    interval = "N/A"
    transfer = "N/A"
    bitrate = "N/A"
    retries = "N/A"

    for line in iperf_lines:
        if 'local' in line:
            # Separate regex patterns for each value
            local_ip_pattern = r'local\s+(\d+\.\d+\.\d+\.\d+)'
            target_ip_pattern = r'to\s+(\d+\.\d+\.\d+\.\d+)'

            # Extract values using the extract_value function
            local_ip = extract_value(local_ip_pattern, line)
            target_ip = extract_value(target_ip_pattern, line)

        if 'sender' in line:
            # Separate regex patterns for each value
            interval_pattern = r'(\d+\.\d+-\d+\.\d+)\s+sec'
            transfer_pattern = r'(\d+)\s+MBytes'
            bitrate_pattern = r'(\d+)\s+Mbits/sec'

            # Extract values using the extract_value function
            interval = extract_value(interval_pattern, line)
            transfer = extract_value(transfer_pattern, line)
            bitrate = extract_value(bitrate_pattern, line)

            # Extract the remaining value (Retr) using a combination of slicing and splitting
            remaining_part = line.split('sender')[0].split('Mbits/sec')[1].strip()
            retries_pattern = r'(\d+)'
            retries = extract_value(retries_pattern, remaining_part)

# Check if any of the values couldn't be found so it can be stored at the logfile
if local_ip == "N/A" or target_ip == "N/A" or interval == "N/A" or transfer == "N/A" or bitrate == "N/A" or retries == "N/A":
    logtype = "WARNING"
    logoutput = f"Local IP:{local_ip};Target IP:{target_ip};Interval:{interval}sec;Transfer:{transfer}Mbytes;Bitrate:{bitrate}Mbits/sec;Retries:{retries}"
    logdescription = "One or more IPerf values couldn't be found"

    print(f"{logdescription}:")
    print(logoutput)

    returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    if returncode[0] == 1:
        write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

# Write the IPerf data to the file
# CSV File Header: Local (IPv4),Target (IPv4),Interval (sec),Transfer (MBytes),Bitrate (Mbits/sec),Retries
# CSV File Vars: local_ip, target_ip, interval, transfer, bitrate, retries
returncode = write_csvfile(filetype_iperf, target_ip, interval, transfer, bitrate, retries, "", "", "", "", "")

logtype = returncode[1]
logdescription = returncode[2]
logoutput = returncode [3]

returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

if returncode[0] == 1:
    write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")


# Use the right Speedtest switches depending on the given Server ID to connect to. By default it selects the best Server at each Test.
try:
    if target_id != None:
        # Run the Speedtest with a specific server ID
        speedtest_output = subprocess.Popen(f'/usr/bin/speedtest --accept-license --accept-gdpr --server-id={target_id}', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    else:
        # Run the Speedtest without a specific server ID
        speedtest_output = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
except Exception as e:
    logtype = "ERROR"
    logoutput = e
    logdescription = "An Error occurred while running the Speedtest"
    speedtest_output = ""

    print(f"{logdescription}:")
    print(logoutput)

    returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    if returncode[0] == 1:
        write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

# Extract Speedtest values
server_pattern = r'\(id:\s+(.*?)\)'
ping_pattern = r'Latency:\s+(.*?)\s'
download_pattern = r'Download:\s+(.*?)\s'
upload_pattern = r'Upload:\s+(.*?)\s'
jitter_pattern = r'Latency:.*?jitter:\s+(.*?)ms'

server = extract_value(server_pattern, speedtest_output)
ping = extract_value(ping_pattern, speedtest_output)
download = extract_value(download_pattern, speedtest_output)
upload = extract_value(upload_pattern, speedtest_output)
jitter = extract_value(jitter_pattern, speedtest_output)

# Check if any of the values couldn't be found so it can be stored at the logfile
if server == "N/A" or ping == "N/A" or download == "N/A" or upload == "N/A" or jitter == "N/A":
    logtype = "WARNING"
    logoutput = f"Server:{server};Ping:{ping}ms;Jitter:{jitter}ms;Download:{download}Mbits/sec;Upload:{upload}Mbits/sec"
    logdescription = "One or more Speedtest values couldn't be found"

    print(f"{logdescription}:")
    print(logoutput)

    returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    if returncode[0] == 1:
        write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

# Write the Speedtest data to the file
# CSV File Header: Server ID,Ping (ms),Jitter (ms),Download (Mbits/sec),Upload (Mbits/sec)
# CSV File Vars: server, ping, jitter, download, upload
returncode = write_csvfile(filetype_speedtest, server, ping, jitter, download, upload, "", "", "", "", "")

logtype = returncode[1]
logdescription = returncode[2]
logoutput = returncode [3]

returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

if returncode[0] == 1:
    write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")


# Write the Combined data to the file
# CSV File Header: IPerf Local (IPv4),IPerf Target (IPv4),IPerf Transfer (MBytes),IPerf Bitrate (Mbits/sec),IPerf Retries,Speedtest Server ID,Speedtest Ping (ms),Speedtest Jitter (ms),Speedtest Download (Mbits/sec),Speedtest Upload (Mbits/sec)
# CSV File Vars: local_ip, target_ip, transfer, bitrate, retries, server, ping, jitter, download, upload
if iperf and target_ip != None:
    returncode = write_csvfile(filetype_combined, local_ip, target_ip, transfer, bitrate, retries, server, ping, jitter, download, upload)

    logtype = returncode[1]
    logdescription = returncode[2]
    logoutput = returncode [3]

    returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

    if returncode[0] == 1:
        write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")


# Write the Logfile entry for finishing the Speedtest
logtype = "INFO"
logoutput = ""
logdescription = "The Speedtest finished successfully"

print(f"{logdescription}:")

returncode = write_csvfile(filetype_log, logtype, logdescription, logoutput, "", "", "", "", "", "", "")

if returncode[0] == 1:
    write_csvfile(filetype_tmplog, logtype, logdescription, logoutput, "", "", "", "", "", "", "")