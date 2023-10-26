## DEPRECIATED (Debian Bullseye)
# ISP-Buster
The ISP-Buster helps you to do Speedtests to an external Server and within your Network and logs them to .csv Files.

This is achieved with a custom Python Program which tests the internal speeds of your Network with Iperf3 and the
external ISP Speeds with speedtest-cli by Ookla.

It is written with Raspberry Pi's in mind and tested on Raspbian OS.</br>
Please consider this if you have troubles using it on a different OS.

Speedtests will be done automatically every 30 minutes initiated by a cronjob as sudo user.</br>
This get's set up by the installer bash script.</br>
Also if you've already got a Crontab with the root user it will get backed up</br>
at /etc/isp-buster/backup/crontab.bak before getting changed by the Script!

It is possible to disable the IPerf3 Speedtest if you're not able to set up an IPerf Host on your Firewall.</br>
You can also define a specific Server for speedtest-cli to keep the results consistent.</br>
These Settings can be adjusted at installation with the installer bash script or by editing the python file</br>
like described in the documentation.

I'm not an expert Coder so use this Repo on your own Risk and don't blame me if you have to reinstall your Raspberry.</br>

If you find something interesting within my Scripts feel free to copy parts of it and implement it into your own code.</br>
Also feel free to contribute to this Repository and make it better :)


----------------------------------------------------------------
----------------------------------------------------------------
# INSTALLATION

    wget https://raw.githubusercontent.com/xXNightstalkerXx/isp-buster/Debian_Bullseye/isp-buster-installer
Download the isp-buster-installer Script with wget

    sudo chmod 0755 isp-buster-installer
To make the Script executable

    ./isp-buster-installer
Launch the Script
</br>
</br>
The Installer does the rest of the Job for you now.

----------------------------------------------------------------
----------------------------------------------------------------
# HOW TO USE

    isp-buster
Launches the speedtest.py python program manually which executes the speedtests and logs them into .csv Files.</br>
The .csv Files are located at /etc/isp-buster/results/ and there are three .csv Files created:
   - "isp-buster_combined.csv" which includes Speedtest Results from IPerf3 and Speedtest-CLI if IPerf is not disabled
   - "isp-buster_speedtest.csv" which includes Speedtest Results just from Speedtest-CLI
   - "isp-buster_iperf.csv" which includes Speedtest Results just from IPerf3 if IPerf is not disabled

There are also logfiles created as .csv Files at /etc/isp-buster/logs/ .</br>
</br>

    isp-buster-uninstaller
Uninstalls the whole ISP-Buster and all it's Files.</br>
Also reverts all changes.
</br>
</br>

    speedtest -L
This command lists all the Ookla Speedtest Servers the Speedtest-CLI can test against.</br>
You will also find the Server ID there used by the Settings within the speedtest.py File.
</br>
</br>

    sudo nano /etc/isp-buster/speedtest.py
To open the Python Script and change the desired Settings for the Script.</br>
Within the Program Header you will find the following Settings:
  - "iperf = False" change this to "True" if you want to set up an IPerf3 Host on your Firewall
  - "target_ip = None" change this to the IPv4 address of your IPerf3 Host
  - "target_id = None" change this to the ID of the Ookla Server you want to be used by speedtest-cli

</br>
</br>
</br>
ATTENTION!!</br>
</br>
DO NOT install the ISP-Buster with the ISP-BUSTER-AUTOINSTALLER and use the ISP-BUSTER-INSTALLER instead!!</br>
The ISP-BUSTER-AUTOINSTALLER is just meant to be used by my RPI-SETUP-TOOL!</br>
</br>

----------------------------------------------------------------
----------------------------------------------------------------
