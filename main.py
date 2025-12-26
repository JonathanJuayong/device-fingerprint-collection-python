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


def get_mac_address(interface_name="Ethernet"):
    """
    Gets the MAC address of a specified network interface.

    :param interface_name: The name of the network interface for which to
        retrieve the MAC address. Defaults to "Ethernet".
    :type interface_name: str
    :return: The MAC address of the specified network interface.
    :rtype: str
    :raises DataCollectionException: If the MAC address of the specified
        network interface is not found.
    """
    mac_address = None
    address = psutil.net_if_addrs()

    # Go through each address and look for one with an interface that matches the interface_name param
    # and family that matches the constant psutil.AF_LINK to get the hardware address
    for interface, addresses_list in address.items():
        if interface == interface_name:
            for address in addresses_list:
                if address.family == psutil.AF_LINK:
                    mac_address = address.address
    if mac_address is None:
        raise DataCollectionException(f"MAC address of {interface_name} not found.")
    else:
        return mac_address


def get_processor_model(operating_system):
    """
    Determines the processor model based on the operating system.

    :param operating_system: The name of the operating system. Supported values are "Windows" and "Linux".
    :type operating_system: str
    :return: The model name of the processor as a string.
    :rtype: str
    :raises UnsupportedOperatingSystemException: If the provided operating system
                                                 is not supported.
    """
    match operating_system:
        case "Windows":
            return cpuinfo.get_cpu_info()["brand_raw"]
        case "Linux":
            terminal_command = "lscpu | grep 'Model name'"
            raw_string = os.popen(terminal_command).read()
            processor_name_as_list = raw_string.strip().split()[2:]
            processor_name_as_string = " ".join(processor_name_as_list)
            return processor_name_as_string
        case _:
            raise UnsupportedOperatingSystemException


def get_active_ports():
    """
    Extracts and retrieves a list of active network ports currently in the 'LISTEN' state.

    :return: A comma-separated string containing all active ports currently in the
        'LISTEN' state.
    :rtype: str
    """
    active_connections = [connection for connection in psutil.net_connections() if connection.status == 'LISTEN']
    active_ports = {str(active_connection.laddr.port) for active_connection in active_connections}
    return ", ".join(active_ports)


def get_internet_speed():
    """
    Determine the download and upload internet speeds by testing against the best available server.

    :return: A string representation of download and upload speeds in Mb/s.
    :rtype: str
    """
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()

    download_speed = st.download() / 1_000_000  # convert to mbps
    upload_speed = st.upload() / 1_000_000

    return f"download: {download_speed:.2f} Mb/s, upload: {upload_speed:.2f} Mb/s"


def collect_data():
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
        device_info = {}
        print("Device data collection starting")

        print("Getting computer name...")
        device_info["computer_name"] = platform.node()
        operating_system = platform.system()
        print("Getting operating system...")
        device_info["operating_system"] = operating_system
        print("Getting processor model...")
        device_info["processor_model"] = get_processor_model(operating_system)

        print("Getting mac address...")
        device_info["mac_address"] = get_mac_address()

        print("Getting computer name...")
        computer_name = socket.gethostname()
        device_info["computer_name"] = computer_name
        print("Getting ip address...")
        device_info["ip_address"] = socket.gethostbyname(computer_name)

        print("Getting system time...")
        device_info["system_time"] = datetime.datetime.now().strftime("%H:%M:%S")
        print("Getting all active ports...")
        device_info["active_ports"] = get_active_ports()

        print("Getting internet download and upload speed...")
        device_info["internet_speed"] = get_internet_speed()

        print("Data collection successful!")
        return device_info
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


def write_to_csv(device_info, file_path):
    file = Path(file_path)
    file.touch(exist_ok=True)

    try:
        print("Preparing to write to file path...")
        with file.open(mode="r+", newline="") as csv_file:
            field_names = device_info.keys()
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)

            if file.stat().st_size > 0:  # if the file is not empty, check for duplicate
                csv_file.seek(0)  # move the cursor to the beginning of the file
                mac_address = device_info["mac_address"]
                has_duplicate = False

                for row in csv_reader:
                    existing_mac_address = row["mac_address"]
                    if mac_address == existing_mac_address:
                        has_duplicate = True
                        break

                if has_duplicate:
                    raise DuplicateDataException
                else:
                    csv_file.seek(0, 2)
                    csv_writer.writerow(device_info)

            else:
                csv_writer.writeheader()
                csv_writer.writerow(device_info)

        print(f"Data successfully written to {file_path}")
    except DuplicateDataException:
        print(f"Error: Writing to {file_path} failed")
        print("Reason: This machine has already been catalogued")
    except PermissionError:
        print(f"Error: Writing to {file_path} failed")
        print(f"Reason: You do not have the permission to read or write this file: {file_path}")
    except Exception as e:
        print(f"Writing to CSV file failed due to unexpected reason: {e}")


if __name__ == '__main__':
    while True:
        file_path = input("Please enter the csv file path: \n").strip()
        if file_path:
            device_info = collect_data()
            write_to_csv(device_info, file_path)
            break
        else:
            print("Invalid file path. Please try again.")
