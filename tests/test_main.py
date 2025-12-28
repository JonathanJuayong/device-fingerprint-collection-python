import csv
import os
import pathlib
import unittest
from unittest.mock import patch, MagicMock

from exeptions import DataCollectionException, UnsupportedOperatingSystemException
from main import getMacAddress, getProcessorModel, getActivePorts, collectData, writeToCSV
from utils import mockNicAddresses, mockMacAddress, mockSConns, mockData, tempFile


class ProjectTest(unittest.TestCase):
    def testGetMacAddressFetchesMacAddress(self):
        """
        Verifies MAC address retrieved by comparing it against a pre-defined mock MAC address.
        """
        addresses = mockNicAddresses()

        testMockAddress = getMacAddress(addresses)
        self.assertEqual(mockMacAddress, testMockAddress)

    def testGetMacAddressRaisesExceptionIfNoMacAddressFound(self):
        """
        Verifies that the `getMacAddress` function raises a `DataCollectionException`
        when no valid MAC address is found in the provided network interface
        address mappings.
        """
        addresses = mockNicAddresses(int1="invalid", int2="invalid")
        with self.assertRaises(DataCollectionException):
            getMacAddress(addresses)

    def testGetProcessorModelRaisesExceptionIfInvalidOperatingSystem(self):
        """
        Tests the `getProcessorModel` function to ensure that it raises the
        `UnsupportedOperatingSystemException` when provided with an invalid
        operating system.
        """
        with self.assertRaises(UnsupportedOperatingSystemException):
            getProcessorModel("Invalid")

    def testGetActivePortsReturnsActivePorts(self):
        """
        Verifies that the function `getActivePorts` correctly identifies and returns the active
        ports from the provided socket connections.
        """
        activePorts = {"443", "5173"}
        testActivePorts = getActivePorts(mockSConns())
        testActivePortsSet = set(testActivePorts.split(", "))
        self.assertEqual(activePorts, testActivePortsSet)

    @patch("main.speedtest.Speedtest")
    def testCollectDataCreatesDictionaryWithExpectedKeys(self, mockSpeedtest):
        """
        Tests that the collectData function correctly creates a dictionary containing
        the expected keys. This verifies that all necessary system and network
        information has been captured.
        """
        # mock speedtest call
        mockSpeedtestObject = MagicMock()
        mockSpeedtestObject.download.return_value = 10000000
        mockSpeedtestObject.upload.return_value = 10000000
        mockSpeedtest.return_value = mockSpeedtestObject
        deviceInfo = collectData()
        deviceInfoKeys = deviceInfo.keys()

        expectedKeys = [
            "computer_name",
            "operating_system",
            "mac_address",
            "processor_model",
            "ip_address",
            "internet_speed",
            "active_ports",
            "system_time"
        ]

        for key in expectedKeys:
            self.assertIn(key, deviceInfoKeys)

    def testWriteToCSVCreatesCSV(self):
        """
        Tests if the `writeToCSV` function successfully creates a CSV file.
        """
        filePath = tempFile("test_file1")
        writeToCSV(mockData(), filePath)

        self.assertTrue(pathlib.Path(filePath).exists())

        os.remove(filePath)

    def testWriteToCSVWritesDataToCSV(self):
        """
        Test case to ensure that the `writeToCSV` function writes the mock data
        to a CSV file correctly.
        """
        filePath = tempFile("test_file2")
        writeToCSV(mockData(), filePath)
        expectedKeys = mockData().keys()

        file = pathlib.Path(filePath)

        with file.open(mode="r") as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                for key in expectedKeys:
                    expectedValue = mockData()[key]
                    actualValue = row[key]
                    print(expectedValue, actualValue)
                    self.assertEqual(expectedValue, actualValue)

        os.remove(filePath)

    def testWriteToCSVShouldNotDuplicateRecord(self):
        """
        Tests that the `writeToCSV` function writes a record to a CSV file only once
        and does not duplicate the record upon repeated calls with the same data.
        """
        filePath = tempFile("test_file3")

        writeToCSV(mockData(), filePath)
        writeToCSV(mockData(), filePath)
        writeToCSV(mockData(), filePath)

        file = pathlib.Path(filePath)

        with file.open(mode="r") as csvFile:
            csvReader = csv.DictReader(csvFile)
            rowCount = list(csvReader)
            self.assertEqual(1, len(rowCount))

        os.remove(filePath)

    def testWriteToCSVShouldUpdateExistingRecordWithNewData(self):
        """
        Tests the functionality of the `writeToCSV` function to ensure that it correctly updates an
        existing record in the CSV file with new data while maintaining data consistency.
        """
        filePath = tempFile("test_file4")

        writeToCSV(mockData(), filePath)
        writeToCSV(mockData(mac="11-22-33-44-55-66"), filePath)

        expectedMacAddresses = [mockData()["mac_address"], "11-22-33-44-55-66"]

        file = pathlib.Path(filePath)

        with file.open(mode="r") as csvFile:
            csvReader = csv.DictReader(csvFile)
            rowCount = list(csvReader)
            self.assertEqual(2, len(rowCount))

            for index, row in enumerate(csvReader):
                expectedValue = expectedMacAddresses[index]
                actualValue = row["mac_address"]
                self.assertEqual(expectedValue, actualValue)

        os.remove(filePath)

if __name__ == "__main__":
    unittest.main()
