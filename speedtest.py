import os
import re
import subprocess
import time

# Function to extract a value from a string using a regex pattern and set to "N/A" if not found
def extract_value(pattern, text):
    match = re.search(pattern, text)
    return match.group(1) if match else "N/A"


# SETTINGS:

# Define the IPv4 to connect to during the Iperf3 Network test and the Server ID to connect to during Speedtest.
# The Server ID can be found by typing "speedtest -L"

iperf = True
target_ip = '10.95.7.1'
target_id = '55754'


# Create the directory if it doesn't exist
results_dir = '/etc/ookla-speedtest/results'
os.makedirs(results_dir, exist_ok=True)

# Run the iperf test
iperf_output = subprocess.Popen('/usr/bin/iperf3 -c ' + target_ip, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

# Split the iperf output into lines
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

# Write the iperf data to the file
try:
    iperf_file = os.path.join(results_dir, 'iperf.csv')
    if not os.path.isfile(iperf_file):
        with open(iperf_file, 'w') as f:
            f.write('Date,Time,Local (IPv4),Target (IPv4),Interval (sec),Transfer (MBytes),Bitrate (Mbits/sec),Retries\r\n')
    with open(iperf_file, 'a+') as f:
        f.write('{},{},{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), local_ip, target_ip, interval, transfer, bitrate, retries))
except Exception as e:
    print(f'An Error occurred while writing to the IPerf File: {e}')

# Run the speedtest
speedtest_output = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr --server-id=' + target_id, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

# Extract speedtest values
ping_pattern = r'Latency:\s+(.*?)\s'
download_pattern = r'Download:\s+(.*?)\s'
upload_pattern = r'Upload:\s+(.*?)\s'
jitter_pattern = r'Latency:.*?jitter:\s+(.*?)ms'

ping = extract_value(ping_pattern, speedtest_output)
download = extract_value(download_pattern, speedtest_output)
upload = extract_value(upload_pattern, speedtest_output)
jitter = extract_value(jitter_pattern, speedtest_output)

# Write the speedtest data to the file
try:
    speedtest_file = os.path.join(results_dir, 'speedtest.csv')
    if not os.path.isfile(speedtest_file):
        with open(speedtest_file, 'w') as f:
            f.write('Date,Time,Ping (ms),Jitter (ms),Download (Mbits/sec),Upload (Mbits/sec)\r\n')
    with open(speedtest_file, 'a+') as f:
        f.write('{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), ping, jitter, download, upload))
except Exception as e:
    print(f'An Error occurred while writing to the Speedtest File: {e}')


# Write the iperf data to the file
try:
    iperf_file = os.path.join(results_dir, 'combined.csv')
    if not os.path.isfile(iperf_file):
        with open(iperf_file, 'w') as f:
            f.write('Date,Time,IPerf Local (IPv4),IPerf Target (IPv4),IPerf Transfer (MBytes),IPerf Bitrate (Mbits/sec),IPerf Retries,Speedtest Server ID,Speedtest Ping (ms),Speedtest Jitter (ms),Speedtest Download (Mbits/sec),Speedtest Upload (Mbits/sec)\r\n')
    with open(iperf_file, 'a+') as f:
        f.write('{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), local_ip, target_ip, transfer, bitrate, retries, target_id, ping, jitter, download, upload))
except Exception as e:
    print(f'An Error occurred while writing to the Combined File: {e}')