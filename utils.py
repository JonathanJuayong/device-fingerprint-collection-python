import tempfile


def mock_data(mac='34-5A-60-22-18-B2'):
    return {
        'active_ports': '7865, 6188, 63903, 139, 5040, 445, 49664, 5563, 32683, 49665, 63342, 135, 41017, 49677, 7680, 5990, 59330, 49668, 5146, 33683, 6189, 1462, 6341, 63344, 19294, 9080, 49669, 63812, 64411, 26822, 54936, 63343, 49670, 49690',
        'computer_name': 'MSI', 'internet_speed': 'download: 82.44 Mb/s, upload: 28.00 Mb/s',
        'ip_address': '192.168.1.102',
        'mac_address': mac, 'operating_system': 'Windows',
        'processor_model': 'Intel(R) Core(TM) i7-14650HX', 'system_time': '19:01:19'
    }


def temp_file(name):
    return f"{tempfile.gettempdir()}\\{name}.csv"
