## This application uses PyQt5 with QtWebkit engine to display user interface. Mode of pins ordering is GPIO.BOARD. This application checks CPU serial number, it can be disabled in Main.py file. 
### UI is displayed with 7 inch touch screen, connected via usb port. Application tested with Rapbian 9 stretch OS.
### Folder schemas contains Sprint Layout file with blueprint of GPIO board. It is ready to make an order to manufacture the GPIO board. GPIO board should be used as you can not connect relays to Rapberry Pi directly. 
Resistor: should be about 1-1.5kOm 
Transistor: 2N3904 (npn) 
Diode: 1N4007 (you could use better one) 
External clock: DS3231 
 
### Required modules:
1) pytz
`sudo pip3 install pytz` 
2) python3-pyqt5, python3-sip 
`sudo apt-get install python3-pyqt5` 
3) PyQt5.QtWebKit 
`sudo apt-get install python3-pyqt5.qtwebkit`

#### App packaging with pyinstaller
`sudo pyinstaller -p /home/pi/Public/modules --add-data '/home/pi/Public/settings.json:.' --add-data '/home/pi/Public/local.db:.' run.py` 
 
#### Autostart
`sudo crontab -e`
Add:
```@reboot /bin/sh -c "export XAUTHORITY=/home/pi/.Xauthority; export DISPLAY=':0.0'; sleep 3; cd /home/pi/Downloads/dist/run; ./run --respawn" > /home/pi/Downloads/c.log 2>&1``` 

#### Desktop shortcut
```sudo nano /home/pi/Desktop/run.desktop

[Desktop Entry]
Name=Пуск
Comment=Пуск приложения
Icon=/usr/share/pixmaps/openbox.xpm
Exec=/bin/sh -c "cd /home/pi/Downloads/dist/run && ./run"
Type=Application
Encoding=UTF-8
Terminal=false
Categories=None;
```

##### How to perform external clock setting
There are only two edits you need to do: 
1. put the below line into the /boot/config.txt file: (edit it with your favourite editor and type the line in - or copy and paste it from here 
 
`dtoverlay=i2c-rtc,ds3231` 
 
2. edit the `lib/udev/hwclock-set` file (`sudo nano /lib/udev/hwclock-set`) and "comment out" the following lines ("comment out" means put a # at the beginning of each of the lines, so they become comments and are ignored by the system) 
 
```
if [ -e /run/systemd/system ] ; then 
exit 0 
fi 
```
so they become: 
```
#if [ -e /run/systemd/system ] ; then 
# exit 0 
#fi 
```
 
...and that's it - that's all you need to do. Shut down your system, connect the rtc module, then power up and test with the command: 
 
`sudo hwclock -r`
