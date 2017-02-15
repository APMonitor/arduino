Installing drivers for the Arduino Uno with Windows7, Vista, or XP:
Plug in your board and wait for Windows to begin it's driver installation process.  After a few moments, the process will fail, despite its best efforts
Click on the Start Menu, and open up the Control Panel.
While in the Control Panel, navigate to System and Security. Next, click on System. Once the System window is up, open the Device Manager.
Look under Ports (COM & LPT).  You should see an open port named "Arduino UNO (COMxx)"
Right click on the "Arduino UNO (COmxx)" port and choose the "Update Driver Software" option.
Next, choose the "Browse my computer for Driver software" option.
Finally, navigate to and select the Uno's driver file, named "Ruggeduino.inf", located on the class website.
Windows will finish up the driver installation from there.