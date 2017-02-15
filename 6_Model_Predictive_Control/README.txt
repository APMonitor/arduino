This is the Arduino Temperature Control Lab.

1.  Unzip/Extract all files from this folder.

2.  The needed Arduino drivers should already be installed.  If not, see the WindowsDriver folder.

3.  Install pyserial and pyqtgraph.  If Anaconda is installed, this can be done by opening a command prompt and typing "conda install pyqtgraph pyserial" or "pip install pyqtgraph pyserial". When asked if you would like to install new packages, press 'y'.

4.  Run main_mpc.py

5.  Collected data will be recorded in the OutputFiles folder under data.xls  Make sure OutputFiles folder exists before starting the program (can lead to an error).

6.  If you encounter a SerialException Access Denied error, unplug and replug your Arduino USB from the computer.