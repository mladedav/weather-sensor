import socket
import ssl
import dht
import machine
import gc
import time
import ntptime

# Credit to mkiotdev https://forum.micropython.org/viewtopic.php?f=16&t=5517&start=10
## Simple software WDT implementation
wdt_counter = 0

def wdt_callback():
    global wdt_counter
    wdt_counter += 1
    if (wdt_counter >= 10):
        machine.reset()

def wdt_feed():
    global wdt_counter
    wdt_counter = 0

wdt_timer = machine.Timer(-1)
wdt_timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=lambda t:wdt_callback())
## END Simple software WDT implementation


# Turn light on Wifi module on during setup
setup_light = machine.Pin(2, machine.Pin.OUT)
setup_light.off()

ENDPOINT = 'data.mladedav.ml/api/v1/weather'
base, relative = ENDPOINT.split('/', 1)

d = dht.DHT11(machine.Pin(0))
l = machine.Pin(16, machine.Pin.OUT)
rtc = machine.RTC()

print(base)
print(relative)

wdt_feed()

while True:
    try:
        # 443 for https. Change 80 for debug and change tls later
        addr_info = socket.getaddrinfo(base, 443)
        addr = addr_info[0][-1]
        break
    except:
        setup_light.on()
        time.sleep(5)
        setup_light.off()

wdt_feed()

setup_light.on()
# End of setup

while True:
    try:
        l.off()
        wdt_feed()
        ntptime.settime()

        now = rtc.datetime()
        d.measure()

        temp = d.temperature()
        hum = d.humidity()
        timestamp = '%04d-%02d-%02dT%02d:%02d:%02d.%03dZ' % (now[0], now[1], now[2], now[4], now[5], now[6], now[7])

        body = '{ "timestamp": "%s", "temperature": %s, "humidity": %s }' % (timestamp, temp, hum)
        content = 'POST /%s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %s\r\n\r\n%s' % (relative, base, len(body), body)
        payload = bytes(content, 'utf8')

        print(content)

        s = socket.socket()
        s.connect(addr)
        tls = ssl.wrap_socket(s, server_hostname=base)
        tls.write(payload)

        r = tls.read(1000)
        print(r)
        tls.close()

        print('done')
    except:
        print('failed')

        # We are not checking the return code. What would we do if it wasn't 200? There is no way

    finally:
        gc.collect()
        l.on()
        wdt_feed()
        time.sleep(60 * 5)
