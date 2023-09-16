import os
import re
import subprocess
import time


# SETTINGS:

# Define the IPv4 to connect to during the Iperf3 Network test and the Server ID to connect to during Speedtest.
# The Server ID can be found by typing "speedtest -L"

iperf = False
target_ip = None
target_id = None


# Function to extract a value from a string using a regex pattern and set to "N/A" if not found
def extract_value(pattern, text):
    match = re.search(pattern, text)
    return match.group(1) if match else "N/A"

# Initialize Exception Variable to find out if and Exception occured and log it.
exception = False

try:
    # Create the results directory if it doesn't exist
    results_dir = '/etc/isp-buster/results'
    os.makedirs(results_dir, exist_ok=True)
    # Create the logs directory if it doesn't exist
    logs_dir = '/etc/isp-buster/logs'
    os.makedirs(results_dir, exist_ok=True)
except Exception as e:
    dir_exc = e
    dir_exc_desc = "An Error occurred while creating the needed directories"
    print("An Error occurred while creating the needed directories:")
    print(e)
    exception = True


# Run the IPerf Test and log it into a .csv File if specified in the Settings
if iperf and target_ip != None:
    try:
        # Run the IPerf test
        iperf_output = subprocess.Popen('/usr/bin/iperf3 -c ' + target_ip, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    except Exception as e:
        iperf_exc = e
        iperf_exc_desc = "An Error occurred while running the IPerf3 Network Speedtest"
        print("An Error occurred while running the IPerf3 Network Speedtest:")
        print(e)
        exception = True
        iperf_output = ""

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
            iperf_val = f"Local IP:{local_ip};Target IP:{target_ip};Interval:{interval}sec;Transfer:{transfer}Mbytes;Bitrate:{bitrate}Mbits/sec;Retries:{retries}"
            iperf_val_desc = "One or more IPerf values couldn't be found"
            print("One or more IPerf values couldn't be found:")
            print(f"Local IP:{local_ip};Target IP:{target_ip};Interval:{interval}sec;Transfer:{transfer}Mbytes;Bitrate:{bitrate}Mbits/sec;Retries:{retries}")
            exception = True

    # Write the IPerf data to the file
    try:
        iperf_file = os.path.join(results_dir, 'iperf.csv')
        if not os.path.isfile(iperf_file):
            with open(iperf_file, 'w') as f:
                f.write('Date,Time,Local (IPv4),Target (IPv4),Interval (sec),Transfer (MBytes),Bitrate (Mbits/sec),Retries\r\n')
        with open(iperf_file, 'a+') as f:
            f.write('{},{},{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), local_ip, target_ip, interval, transfer, bitrate, retries))
    except Exception as e:
        iperf_file_exc = e
        iperf_file_exc_desc = "An Error occurred while writing to the iperf.csv File"
        print("An Error occurred while writing to the iperf.csv File:")
        print(e)
        exception = True


# Use the right Speedtest switches depending on the given Server ID to connect to. By default it selects the best Server at each Test.
try:
    if target_id != None:
        # Run the Speedtest with a specific server ID
        speedtest_output = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr --server-id=' + target_id, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    else:
        # Run the Speedtest without a specific server ID
        speedtest_output = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
except Exception as e:
    speedt_exc = e
    speedt_exc_desc = "An Error occurred while running the Speedtest"
    print("An Error occurred while running the Speedtest:")
    print(e)
    exception = True
    speedtest_output = ""

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
    speedt_val = f"Server:{server};Ping:{ping}ms;Jitter:{jitter}ms;Download:{download}Mbits/sec;Upload:{upload}Mbits/sec"
    speedt_val_desc = "One or more Speedtest values couldn't be found"
    print("One or more Speedtest values couldn't be found:")
    print(f"Server:{server};Ping:{ping}ms;Jitter:{jitter}ms;Download:{download}Mbits/sec;Upload{upload}Mbits/sec")
    exception = True

# Write the Speedtest data to the file
try:
    speedtest_file = os.path.join(results_dir, 'speedtest.csv')
    if not os.path.isfile(speedtest_file):
        with open(speedtest_file, 'w') as f:
            f.write('Date,Time,Server ID,Ping (ms),Jitter (ms),Download (Mbits/sec),Upload (Mbits/sec)\r\n')
    with open(speedtest_file, 'a+') as f:
        f.write('{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), server, ping, jitter, download, upload))
except Exception as e:
    speedt_file_exc = e
    speedt_file_exc_desc = "An Error occurred while writing to the speedtest.csv File"
    print("An Error occurred while writing to the speedtest.csv File:")
    print(e)
    exception = True


# Write the Combined data to the file
if iperf and target_ip != None:
    try:
        combined_file = os.path.join(results_dir, 'combined.csv')
        if not os.path.isfile(combined_file):
            with open(combined_file, 'w') as f:
                f.write('Date,Time,IPerf Local (IPv4),IPerf Target (IPv4),IPerf Transfer (MBytes),IPerf Bitrate (Mbits/sec),IPerf Retries,Speedtest Server ID,Speedtest Ping (ms),Speedtest Jitter (ms),Speedtest Download (Mbits/sec),Speedtest Upload (Mbits/sec)\r\n')
        with open(combined_file, 'a+') as f:
            f.write('{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(time.strftime('%d/%m/%y'), time.strftime('%H:%M'), local_ip, target_ip, transfer, bitrate, retries, server, ping, jitter, download, upload))
    except Exception as e:
        comb_file_exc = e
        comb_file_exc_desc = "An Error occurred while writing to the combined.csv File"
        print("An Error occurred while writing to the combined.csv File:")
        print(e)
        exception = True


# Write the Logs into the Logfile