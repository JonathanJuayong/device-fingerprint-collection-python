import platform
import cpuinfo
import os
import psutil
import socket
import datetime
import speedtest


def get_mac_address(interface_name="Ethernet"):
    mac_address = None
    address = psutil.net_if_addrs()
    for interface, addresses_list in address.items():
        if interface == interface_name:
            for address in addresses_list:
                if address.family == psutil.AF_LINK:
                    mac_address = address.address

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
            raise Exception("Unsupported operating system")


def get_active_ports():
    active_connections = [connection for connection in psutil.net_connections() if connection.status == 'LISTEN']
    active_ports = {str(active_connection.laddr.port) for active_connection in active_connections}
    return ", ".join(active_ports)


def get_internet_speed():
    try:
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()

        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000

        return f"download: {download_speed:.2f} Mb/s, upload: {upload_speed:.2f} Mb/s"
    except Exception as e:
        print(e)


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

    device_info = {}

    operating_system = platform.system()
    device_info["operating_system"] = operating_system
    device_info["processor_model"] = get_processor_model(operating_system)

    device_info["mac_address"] = get_mac_address()

    computer_name = socket.gethostname()
    device_info["computer_name"] = computer_name
    device_info["ip_address"] = socket.gethostbyname(computer_name)

    device_info["system_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    device_info["active_ports"] = get_active_ports()

    device_info["internet_speed"] = get_internet_speed()
    return device_info


if __name__ == '__main__':
    pass
    # print(operating_system)
    # print(platform.node())
