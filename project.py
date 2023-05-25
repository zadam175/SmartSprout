import datetime
import time
import board
import Adafruit_DHT
from gpiozero import MCP3008, OutputDevice
from picamera import PiCamera
import os
import requests
import serial

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
light_sensor = MCP3008(channel=0)
soil_moisture_sensor = MCP3008(channel=2)
RELAY_PIN = 27
pump = OutputDevice(RELAY_PIN)
camera = PiCamera()
camera.rotation = 180

# Constants
LIGHT_LOW_THRESHOLD = 0.200
LIGHT_HIGH_THRESHOLD = 0.750
SOIL_DRY_THRESHOLD = 0.004
SOIL_WET_THRESHOLD = 0.09
TEMP_LOW_THRESHOLD = 17
TEMP_HIGH_THRESHOLD = 39
HUMIDITY_LOW_THRESHOLD = 49
HUMIDITY_HIGH_THRESHOLD = 71


last_five_photos = []

def send_warning_to_flask_stats(warnings):
	url = "https://smartsprout.azurewebsites.net/stats"
	payload = {"warnings": warnings}
	response = requests.post(url, json=payload)
	if response.status_code != 200:
		print("Failed to send data to Flask app")
			

def take_photo():
	timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	filename = f"photo_{timestamp}.jpg"
	try:
		camera.capture(filename)
	except Exception as e:
		print(f"Failed to capture photo: {e}")
		return None

	last_five_photos.append(filename)

	return filename

def send_photo_to_flask(filename):
	url = "https://smartsprout.azurewebsites.net/upload"
	files = {"photo": open(filename, "rb")}
	response = requests.post(url, files=files)
	if response.status_code != 200:
		print("Failed to send photo to Flask app")
		
ser = serial.Serial('/dev/ttyACM1', 9600)
time.sleep(2)

def main():
	last_photo_hour = None
	last_watered = None
	try:
		while True:
			print("Reading sensor data...")
			humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
			light_level = light_sensor.value
			soil_moisture_level = soil_moisture_sensor.value
			print(f"Humidity: {humidity}, Temperature: {temperature}, Light level: {light_level}, Soil Moisture level: {soil_moisture_level}")
			
			sensor_data_str = f"{humidity}, {temperature}, {light_level}, {soil_moisture_level}\n"
			ser.write(f"{sensor_data_str}".encode())
			
			data = {
				"moisture": soil_moisture_level,
				"temp": temperature,
				"humidity": humidity,
				"light": light_level,
			}
			
			warnings = []

			if temperature < TEMP_LOW_THRESHOLD:
				print("Temperature is below the threshold")
				warnings.append("Your plant is freezing! Let's go warm them up")
			elif temperature > TEMP_HIGH_THRESHOLD:
				print("Temperature is above the threshold")
				warnings.append("Your plant is sweating it out right now! Let's go cool them down")

			if humidity < HUMIDITY_LOW_THRESHOLD:
				print("Humidity is below the threshold")
				warnings.append("It's not humid enough in here!")
			elif humidity > HUMIDITY_HIGH_THRESHOLD:
				print("Humidity is above the threshold")
				warnings.append("It's too humid in here!")

			hour = datetime.datetime.now().hour
			if  7<= hour < 19:
				if light_level < LIGHT_LOW_THRESHOLD:
					print("Light level is below the threshold")
					warnings.append("It's way too dark in here right now")
				elif light_level > LIGHT_HIGH_THRESHOLD:
					print("Light level is above the threshold")
					warnings.append("It's too bright in here!")

			if soil_moisture_level < SOIL_DRY_THRESHOLD:
				print("Soil Mositure is below the threshold")
				if last_watered is None or time.time() - last_watered > 600:
					pump.on()
					time.sleep(5)
					pump.off()
					last_watered = time.time()
				warnings.append("I'm so thirsty")
			elif soil_moisture_level > SOIL_WET_THRESHOLD:
				print("Soil Moisture is above the threshold")
				warnings.append("I've been watered too much!!")
				
			if hour % 6 == 0 and last_photo_hour != hour:
				filename = take_photo()
				print(f"New photo taken: {filename}, current list of photos: {last_five_photos}")
				if filename is not None:
					send_photo_to_flask(filename)
					last_photo_hour = hour
					if len(last_five_photos) > 5:
						oldest_photo = last_five_photos.pop(0)
						print(f"Deleting photo: {oldest_photo}")
						os.remove(oldest_photo)
						print("Photo removed successfully")
			
			send_warning_to_flask_stats(warnings)
			
			#testing + demo timing 
			#time.sleep(10)
			#actual project timing 
			time.sleep(60 * 15)
	except KeyboardInterrupt:
		print("Program interrupted")
	finally:
		pump.close()
		camera.close()
		ser.close()
		print("Cleanup complete")

if __name__ == "__main__":
	main()
