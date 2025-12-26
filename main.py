import platform
import cpuinfo
import os
import psutil
import socket
import datetime
import speedtest

from errors import UnsupportedOperatingSystemException, DataCollectionException


def get_mac_address(interface_name="Ethernet"):
    mac_address = None
    address = psutil.net_if_addrs()
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
    active_connections = [connection for connection in psutil.net_connections() if connection.status == 'LISTEN']
    active_ports = {str(active_connection.laddr.port) for active_connection in active_connections}
    return ", ".join(active_ports)


def get_internet_speed():
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()

    download_speed = st.download() / 1_000_000
    upload_speed = st.upload() / 1_000_000

    return f"download: {download_speed:.2f} Mb/s, upload: {upload_speed:.2f} Mb/s"


def collect_data():
    """
       This function collects the following information from this device:
       - computer name
       - ip address
       - mac address
       - processor model
       - operating System
       - system time
       - internet connection speed
       - active ports
       and returns a dictionary containing the above information
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


if __name__ == '__main__':
    pass
    # print(operating_system)
    # print(platform.node())
