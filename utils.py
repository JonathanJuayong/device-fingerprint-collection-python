import tempfile
from socket import AddressFamily

import psutil

mockMacAddress = "34-5A-60-22-18-B2"


class MockSnicaddr:
    def __init__(self,
                 address=mockMacAddress,
                 netmask="255.255.255.0",
                 ptp=None,
                 broadcast=None,
                 family=psutil.AF_LINK):
        self.family = family
        self.address = address
        self.netmask = netmask
        self.ptp = ptp
        self.broadcast = broadcast


class MockSConn:
    def __init__(self, port, status="NONE"):
        self.status = status
        self.laddr = type("", (), {"port": port})()


def mockSConns():
    return [
        MockSConn(port=80),
        MockSConn(port=443, status="LISTEN"),
        MockSConn(port=8080),
        MockSConn(port=1337),
        MockSConn(port=5173, status="LISTEN"),
        MockSConn(port=123),
    ]


def mockData(mac="34-5A-60-22-18-B2"):
    return {
        "active_ports": "7865, 6188, 63903, 139, 5040, 445, 49664, 5563, 32683, 49665, 63342, 135, 41017, 49677, 7680, 5990, 59330, 49668, 5146, 33683, 6189, 1462, 6341, 63344, 19294, 9080, 49669, 63812, 64411, 26822, 54936, 63343, 49670, 49690",
        "computer_name": "MSI", "internet_speed": "download: 82.44 Mb/s, upload: 28.00 Mb/s",
        "ip_address": "192.168.1.102",
        "mac_address": mac, "operating_system": "Windows",
        "processor_model": "Intel(R) Core(TM) i7-14650HX", "system_time": "19:01:19"
    }


def mockNicAddresses(int1="Ethernet", int2="Bluetooth Network Connection"):
    return {
        int1: [
            MockSnicaddr(),
            MockSnicaddr(address="test1", family=AddressFamily.AF_INET6),
            MockSnicaddr(address="test2", family=AddressFamily.AF_INET),
        ],
        int2: [
            MockSnicaddr(address="11-22-33-44-55-66"),
            MockSnicaddr(address="test3", family=AddressFamily.AF_INET6),
            MockSnicaddr(address="test4", family=AddressFamily.AF_INET),
        ]
    }


def tempFile(name):
    return f"{tempfile.gettempdir()}\\{name}.csv"
