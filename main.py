from machine import Pin
import dht
import time
from ntptime import settime
import network
import urequests

from connection import ssid, password, room, path, access_key
utc_offset = -7

led = Pin(15, Pin.OUT)
sensor = dht.DHT11(Pin(12))

# Turns the LED on and off in successions
def do_led_blinky(blinkType):
	def rapid_blink(num):
		for i in range(num):
			time.sleep(0.08)
			led.on()
			time.sleep(0.08)
			led.off()
	if blinkType == "SINGLE":
		rapid_blink(1)
	elif blinkType == "QUADRUPLE":
		rapid_blink(4)
	elif blinkType == "HOLD_DOUBLE":
		led.on()
		time.sleep(0.5)
		led.off()
		rapid_blink(2)

# Establishes connection to wifi
def connect_wifi():
	print("Connecting to wifi")
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	if not wlan.isconnected():
		wlan.connect(ssid, password)
		while not wlan.isconnected():
			print(".", end="")
			time.sleep(1)
		print()
	print("Connected")
	do_led_blinky("QUADRUPLE")

# Disconnects the current wifi connection
def disconnect_wifi():
	wlan = network.WLAN(network.STA_IF)
	if wlan.isconnected():
		wlan.disconnect()
	wlan.active(False)

# Resets the system clock by pinging an NTP server
def reset_time():
	print("Getting current time")
	try:
		settime()
		return True
	except OSError as e:
		print("Unable to get the current time")

# Returns the current time adjusted for timezone
def get_current_time():
	return time.localtime(time.time() + (utc_offset * 3600))

# Reads and returns current temperature and humidity
def read_sensor():
	print("Reading sensor")
	try:
		sensor.measure()
		temp = sensor.temperature()
		humidity = sensor.humidity()
		return temp, humidity
	except OSError as e:
		print("Failed to read sensor")
		return None, None

# Sleeps for x amount of minutes, not a deep sleep but hey it works
def take_nap(min):
	disconnect_wifi()
	minutes_until_next_hour = 60 - min + 0.15
	print(f"Taking a nap for {minutes_until_next_hour} minutes")
	time.sleep(60 * minutes_until_next_hour)

initialized = False
previousHourRecorded = -1

while True:
	# Connect to wifi. Verify that system clock was indeed set.
	connect_wifi()
	time_successfully_set = reset_time()
	if time_successfully_set:
		# Get current time. If not initialized, then wait until the top of the hour unless it happens to be so.
		# Otherwise check if the current hour is greater than the previous hour recorded.
		print(get_current_time())
		do_led_blinky("SINGLE")
		current_time = get_current_time()
		if not initialized:
			initialized = True
			previousHourRecorded = current_time[3] if (current_time[4] > 0) else -1
		if current_time[3] > previousHourRecorded:
			# Read sensor data and verify that data was returned.
			temp, humidity = read_sensor()
			if not (temp is None):
				# Send the data to a web api.
				print("Sending data")
				do_led_blinky("SINGLE")
				dataPacket = {
					"Rm" : room,
					"Ti" : f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:00:00",
					"Te" : temp,
					"Hu" : humidity
				}
				response = None
				try:
					response = urequests.post(path, headers = {"Content-Type" : "application/json", "AccessKey" : access_key}, json = dataPacket)
				except OSError as e:
					print("Failed to post data")
				if not (response is None):
					response.close()
					if response.status_code in [200, 201]:
						# Data was successfully sent! Increment previousHourRecorded and sleep until the next top of the hour
						print("Successfully uploaded data")
						do_led_blinky("HOLD_DOUBLE")
						previousHourRecorded = current_time[3] if (current_time[3] < 23) else -1
						take_nap(current_time[4] + current_time[5]/60)
						continue
		else:
			take_nap(current_time[4] + current_time[5]/60)
			continue
	time.sleep(7)