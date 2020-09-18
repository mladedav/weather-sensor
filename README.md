I am using NodeMCU esp8266
From https://micropython.org/download/esp8266/ download v1.13

esptool.py erase_flash
esptool.py --port COM5 --baud 460800 write_flash --flash_size=detect 0 .\esp8266-20200911-v1.13.bin

cd src
ampy -p COM5 ls
ampy -p COM5 get boot.py > ./original-boot.py
ampy -p COM5 put boot.py
ampy -p COM5 run main.py

For interactive prompt use tera term. Change baud rate of serial port to 115200.
