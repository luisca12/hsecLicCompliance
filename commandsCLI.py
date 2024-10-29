from netmiko import ConnectHandler
from log import authLog
from functions import failedDevices, logInCSV

import traceback

shHostname = "show run | i hostname"
shLicSumm = "show license summary"

def complCheck(validIPs, username, netDevice):
    # This function is to check for compliance

    for validDeviceIP in validIPs:
        missingConfig1 = False
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'Outputs/netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"INFO: Connecting to device {validDeviceIP}...")
            authLog.info(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                try:
                    authLog.info(f"Connected to device {validDeviceIP}")
                    sshAccess.enable()
                    shHostnameOut = sshAccess.send_command(shHostname)
                    authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                    shHostnameOut = shHostnameOut.split(' ')[1]
                    shHostnameOut = shHostnameOut + "#"

                    print(f"INFO: Taking a \"{shLicSumm}\" for device: {validDeviceIP}")
                    shLicSummOut = sshAccess.send_command(shLicSumm)
                    authLog.info(f"Automation successfully ran the command:{shLicSumm}\n{shHostnameOut}{shLicSumm}\n{shLicSummOut}")
                    print(f"{shHostnameOut}{shLicSumm}\n{shLicSummOut}")
                        
                    if "DNA_HSEC" in shLicSummOut:
                        authLog.info(f"Device {validDeviceIP} has the DNA_SEC license")
                        print(f"INFO: Device {validDeviceIP} has the DNA_SEC license")
                        logInCSV(validDeviceIP, "Devices with DNA HSEC License")
                    else:
                        authLog.info(f"Device {validDeviceIP} is missing the DNA_SEC license.")
                        print(f"INFO: Device {validDeviceIP} is missing the DNA_SEC license")
                        logInCSV(validDeviceIP, "Devices missing DNA HSEC License")

                except Exception as error:
                    print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                    authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
                    failedDevices(username, validDeviceIP, error)

        except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            failedDevices(username, validDeviceIP, error)