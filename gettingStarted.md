# Getting Started

Follow these steps to set up your Temperature Control Lab:

1. Install Anaconda  

    [Anaconda](https://www.anaconda.com/download/) is the recommended Python environment for using the Temperature Control Lab.  Once you have installed the correct of Anaconda version for your system, the remaining required packages can be installed using the following command in your command line or terminal.

    ```
    conda install -y pyqtgraph pyserial
    ```

2. Install tclab Python package

    ```
    pip install tclab
    ```

3. Clone Repository  

    The next step is to clone the repository containing the Python code for the lab.  This can be done either using the clone button above, or by using the command 

    ```
    git clone https://github.com/APMonitor/arduino.git
    ```

4. Plug in Arduino  

    Plug the Arduino with the lab attached into your computer via the USB connection.  Plug the DC adapter into the wall.


5.  Install Arduino Drivers  

    *If you are using Windows 10, the Arduino board should connect without additional drivers required.*  

    If you are using a different version of Windows, see the [driver installation instructions](WindowsDriver/Readme.txt).
    
    Mac OS X users may need to install a serial driver. For arduino clones using the CH340G, CH34G or CH34X chipset, a suitable driver can be found at [https://github.com/MPParsley/ch340g-ch34g-ch34x-mac-os-x-driver](https://github.com/MPParsley/ch340g-ch34g-ch34x-mac-os-x-driver).


6.  Install Arduino Firmware

    If you are using your own Arduino board, you will need to flash the board with the custom firmware used by the lab.  This is done using the [Arduino IDE](https://www.arduino.cc/en/Main/Software).  The script that must be uploaded to the board is found [here](/ArduinoFirmware/ArduinoFirmware/ArduinoFirmware.ino).

7. Run Python scripts

    Your temperature control lab should be ready to run.  Example scripts for various activities such as step tests, data collection and control are included in the repository, and can be run using the included main*.py scripts in each subfolder.
