import socket
import ssl
import dht
import machine
import gc
import time
import ntptime

# Turn light on Wifi module on during setup
setup_light = machine.Pin(2, machine.Pin.OUT)
setup_light.off()

ENDPOINT = 'data.mladedav.ml/api/v1/weather'
base, relative = ENDPOINT.split('/', 1)

d = dht.DHT11(machine.Pin(0))
l = machine.Pin(16, machine.Pin.OUT)
rtc = machine.RTC()
ntptime.settime()

while True:
    try:
        # 443 for https. Change 80 for debug and change tls later
        addr_info = socket.getaddrinfo(base, 443)
        addr = addr_info[0][-1]
        break
    except:
        time.sleep(5)

setup_light.on()
# End of setup

while True:
    l.off()

    try:
        now = rtc.datetime()
        timestamp = '%04d-%02d-%02dT%02d:%02d:%02d.%03dZ' % (now[0], now[1], now[2], now[4], now[5], now[6], now[7])
        d.measure()
        temp = d.temperature()
        hum = d.humidity()

        body = '{ "timestamp": "%s", "temperature": %s, "humidity": %s }' % (timestamp, temp, hum)
        content = 'POST /%s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %s\r\n\r\n%s' % (relative, base, len(body), body)
        payload = bytes(content, 'utf8')

        print(content)

        s = socket.socket()
        s.connect(addr)
        tls = ssl.wrap_socket(s)
        tls.write(payload)
        s.close()
        # We are not checking the return code. What would we do if it wasn't 200? There is no way

    except:
        print('Failed')
    finally:
        gc.collect()
        l.on()
        # wait for 5 minutes
        # This will get skewed by the process itself but hey, who cares, right?
        time.sleep(5 * 60)
