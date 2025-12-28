import multiprocessing
import platform
import cpuinfo
import os
import psutil
import socket
import datetime
import speedtest
import csv
from pathlib import Path
from exeptions import UnsupportedOperatingSystemException, DataCollectionException, DuplicateDataException


def getMacAddress(address):
    """
    Gets the MAC address of a network interface.

    :raises DataCollectionException: If no MAC address can be identified for the
      specified prefixes.
    :return: The MAC address of the discovered network interface.
    :rtype: str
    """
    macAddress = None
    prefixes = ["eth", "en", "wlan", "wl", "l"]  # common network interface prefixes

    # Go through each address and look for one with an interface that matches the prefixes
    # and family that matches the constant psutil.AF_LINK to get the hardware address
    for interface, addressesList in address.items():
        if any([interface.lower().startswith(prefix) for prefix in prefixes]):
            for address in addressesList:
                if address.family == psutil.AF_LINK:
                    macAddress = address.address
            break
    if macAddress is None:
        raise DataCollectionException("No MAC address found.")
    else:
        return macAddress


def getProcessorModel(operatingSystem):
    """
    Determines the processor model based on the operating system.

    :param operatingSystem: The name of the operating system. Supported values are "Windows" and "Linux".
    :type operatingSystem: str
    :return: The model name of the processor as a string.
    :rtype: str
    :raises UnsupportedOperatingSystemException: If the provided operating system
                                                 is not supported.
    """
    match operatingSystem.strip():
        case "Windows":
            return cpuinfo.get_cpu_info()["brand_raw"]
        case "Linux":
            terminalCommand = "lscpu | grep 'Model name'"
            rawString = os.popen(terminalCommand).read()
            processorNamesAsList = rawString.strip().split()[2:]
            processorNameAsString = " ".join(processorNamesAsList)
            return processorNameAsString
        case _:
            raise UnsupportedOperatingSystemException


def getActivePorts(connections):
    """
    Extracts and retrieves a list of active network ports currently in the 'LISTEN' state.

    :return: A comma-separated string containing all active ports currently in the
        'LISTEN' state.
    :rtype: str
    """
    activeConnections = [connection for connection in connections if connection.status == 'LISTEN']
    activePorts = {str(activeConnection.laddr.port) for activeConnection in activeConnections}
    return ", ".join(activePorts)


def getInternetSpeed():
    """
    Determine the download and upload internet speeds by testing against the best available server.

    :return: A string representation of download and upload speeds in Mb/s.
    :rtype: str
    """
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()

    downloadSpeed = st.download() / 1_000_000  # convert to mbps
    uploadSpeed = st.upload() / 1_000_000

    return f"download: {downloadSpeed:.2f} Mb/s, upload: {uploadSpeed:.2f} Mb/s"


def collectData():
    """
    Retrieves the following information:
    - computer name
    - operating system
    - processor model
    - MAC address
    - IP address
    - system time
    - active ports
    - internet speed (upload and download)
    The data is returned as a dictionary.

    :raises UnsupportedOperatingSystemException: If the operating system
        is neither Linux nor Windows.
    :raises DataCollectionException: If any data collection step fails.
    :raises TimeoutError: If the function takes too long to complete its execution.
    :raises Exception: For any general unexpected errors encountered during execution.
    :return: A dictionary containing the collected device information.
    :rtype: dict
    """
    try:
        deviceInfo = {}
        print("Device data collection starting")

        operatingSystem = platform.system()
        print("Getting operating system...")
        deviceInfo["operating_system"] = operatingSystem
        print("Getting processor model...")
        deviceInfo["processor_model"] = getProcessorModel(operatingSystem)

        print("Getting mac address...")
        deviceInfo["mac_address"] = getMacAddress(psutil.net_if_addrs())

        print("Getting computer name...")
        computerName = socket.gethostname()
        deviceInfo["computer_name"] = computerName
        print("Getting ip address...")
        deviceInfo["ip_address"] = socket.gethostbyname(computerName)

        print("Getting system time...")
        deviceInfo["system_time"] = datetime.datetime.now().strftime("%H:%M:%S")
        print("Getting all active ports...")
        deviceInfo["active_ports"] = getActivePorts(psutil.net_connections())

        print("Getting internet download and upload speed...")
        deviceInfo["internet_speed"] = getInternetSpeed()

        print("Data collection successful!")
        return deviceInfo
    except UnsupportedOperatingSystemException:
        print("This program only supports Linux and Windows.")
    except DataCollectionException as e:
        print(e)
        print("Data collection failed")
    except TimeoutError:
        print("Program took too long to finish.")
    except Exception as e:
        print(e)
        print("Program failed due to unexpected error.")


def writeToCSV(deviceInfo, filePath):
    """
    Writes device information to a CSV file. This function accepts a dictionary containing
    device information and a file path to write the data.

    :param deviceInfo: A dictionary containing device information.
    :type deviceInfo: Dict[str, Any]
    :param filePath: The file path of the CSV file where data will be written. If the file
        does not exist, it will be created.
    :type filePath: str
    :return: None
    :raises DuplicateDataException: If a device with the same `mac_address` already exists
        in the specified file.
    :raises PermissionError: If there are insufficient permissions to read or write the file.
    :raises Exception: For any unexpected errors that may occur during file operations.
    """
    file = Path(filePath)
    file.touch(exist_ok=True)

    try:
        print("Preparing to write to file path...")
        with file.open(mode="r+", newline="") as csvFile:
            fieldNames = deviceInfo.keys()
            csvReader = csv.DictReader(csvFile)
            csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames)

            if file.stat().st_size > 0:  # if the file is not empty, check for duplicate
                csvFile.seek(0)  # move the cursor to the beginning of the file
                macAddress = deviceInfo["mac_address"]
                hasDuplicate = False

                for row in csvReader:
                    existingMacAddress = row["mac_address"]
                    if macAddress == existingMacAddress:
                        hasDuplicate = True
                        break

                if hasDuplicate:
                    raise DuplicateDataException
                else:
                    csvFile.seek(0, 2)
                    csvWriter.writerow(deviceInfo)

            else:
                csvWriter.writeheader()
                csvWriter.writerow(deviceInfo)

        print(f"Data successfully written to {filePath}")
    except DuplicateDataException:
        print(f"Error: Writing to {filePath} failed")
        print("Reason: This machine has already been catalogued")
    except PermissionError:
        print(f"Error: Writing to {filePath} failed")
        print(f"Reason: You do not have the permission to read or write this file: {filePath}")
    except Exception as e:
        print(f"Writing to CSV file failed due to unexpected reason: {e}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    while True:
        filePath = input("Please enter the csv file path: \n").strip()
        if filePath:  # check if the user has entered an empty string
            deviceInfo = collectData()
            writeToCSV(deviceInfo, filePath)
            break
        else:
            print("Invalid file path. Please try again.")
