#!/usr/bin/env python3
import RPi.GPIO as GPIO
import logging
import time

from prometheus_client import Counter, start_http_server
from systemd.journal import JournalHandler

# Setup logging to the Systemd Journal
log = logging.getLogger('gas_sensor')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

# Initialize the DHT22 sensor
# Read data from GPIO4 pin on the Raspberry Pi
SENSOR_PIN = 23

# The time in seconds between sensor reads
READ_INTERVAL = 0.1

# Create Prometheus counter  for humidity and temperature in
# Celsius and Fahrenheit
ct = Counter(name='gmbd_counter', documentation='Impulse counter',labelnames=['impulse'])

# Initialize the labels for the temperature scale
ct.labels('impulse')

# Raspberry GPIO Configuration
gpiopin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpiopin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

count = 0
previous = "null"
def read_sensor():
    global previous
    global count
    state = GPIO.input(gpiopin)

    #log.info("Counter :{} {}".format(count,previous))
    if state == False and previous == "open" or state == False and previous == "null":
        previous = "closed"
        ct.labels('impulse').inc()
        count+=1
    if state != False and previous == "closed" or state != False and previous == "null":
        previous = "open"

    time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    # Expose metrics
    metrics_port = 8000
    start_http_server(metrics_port)
    print("Serving sensor metrics on :{}".format(metrics_port))
    log.info("Serving sensor metrics on :{}".format(metrics_port))

    previous = "null"
    while True:
        read_sensor()
    GPIO.cleanup(gpiopin)
