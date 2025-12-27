# Automation - Device Information Collector

This project is a Python-based automation tool designed to collect various hardware and network information from a computer and save it to a CSV file. It is particularly useful for cataloging devices and their specifications.

## Features

The tool collects the following information:
- Computer Name
- Operating System
- Processor Model
- MAC Address
- IP Address
- System Time
- Active Ports
- Internet Speed (Download and Upload)

It also includes:
- Duplicate detection based on MAC address.
- Support for Windows and Linux.
- Error handling for unsupported operating systems and data collection issues.

## Prerequisites

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository or download the source code.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the `main.py` script:
   ```bash
   python main.py
   ```
2. When prompted, enter the path to the CSV file where you want to save the data (e.g., `device_info.csv`).
3. The script will collect the data and append it to the CSV file. If the file doesn't exist, it will be created with a header row.

## Project Structure

- `main.py`: The main entry point of the application.
- `exeptions.py`: Custom exception classes.
- `utils.py`: Utility functions.
- `requirements.txt`: List of Python dependencies.

## Troubleshooting

- **UnsupportedOperatingSystemException**: This tool currently supports only Windows and Linux.
- **DuplicateDataException**: The tool will not add information for a device that has already been cataloged in the same CSV file (checked via MAC address).
- **PermissionError**: Ensure you have read/write permissions for the specified CSV file path.
