from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import traceback
import os

app = Flask(__name__, static_folder='static')

# Global variables to hold the sensor data
moisture = None
temp = None
humidity = None
light = None
warnings = []

@app.route('/particle', methods=['POST'])
def particle():
    try:
        data = request.get_json()
        print('Data type:', type(data))  # Debugging statement
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid payload'}), 400

        # Split the data string and assign values to keys
        values = data['data'].split(', ')
        data_dict = {
            'humidity': values[0],
            'temp': values[1],
            'light': values[2],
            'moisture': values[3]
        }
        
        print('Data received from Particle:', data_dict)

        global moisture, temp, humidity, light
        moisture = data_dict.get('moisture')
        temp = data_dict.get('temp')
        humidity = data_dict.get('humidity')
        light = data_dict.get('light')

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        traceback.print_exc()
        print('Exception occurred:', str(e))
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/data', methods=['GET'])
def data():
    moisture_str = format(float(moisture), '.5f') if moisture is not None and moisture.replace('.', '', 1).isdigit() else None
    temp_str = format(float(temp), '.2f') if temp is not None and temp.replace('.', '', 1).isdigit() else None
    humidity_str = format(float(humidity), '.2f') if humidity is not None and humidity.replace('.', '', 1).isdigit() else None
    light_str = format(float(light), '.2f') if light is not None and light.replace('.', '', 1).isdigit() else None

    data_dict = {
        'moisture': moisture_str,
        'temp': temp_str,
        'humidity': humidity_str,
        'light': light_str,
        'warnings': warnings,
    }

    return jsonify(data_dict), 200

@app.route('/', methods=['GET', 'POST']) 
def index():
    moisture_str = format(float(moisture), '.5f') if moisture is not None and moisture.replace('.', '', 1).isdigit() else None
    temp_str = format(float(temp), '.2f') if temp is not None and temp.replace('.', '', 1).isdigit() else None
    humidity_str = format(float(humidity), '.2f') if humidity is not None and humidity.replace('.', '', 1).isdigit() else None

    data_dict = {
        'moisture': moisture_str,
        'temp': temp_str,
        'humidity': humidity_str,
    }

    return render_template('index.html', data=data_dict)  # Pass data to template  

@app.route('/home', methods=['GET', 'POST'])
def home():
    moisture_str = format(float(moisture), '.5f') if moisture is not None and moisture.replace('.', '', 1).isdigit() else None
    temp_str = format(float(temp), '.2f') if temp is not None and temp.replace('.', '', 1).isdigit() else None
    humidity_str = format(float(humidity), '.2f') if humidity is not None and humidity.replace('.', '', 1).isdigit() else None

    data_dict = {
        'moisture': moisture_str,
        'temp': temp_str,
        'humidity': humidity_str,
    }

    return render_template('Home.html', data=data_dict)  # Pass data to template  

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    global warnings
    if request.method == 'POST':
        payload = request.get_json()
        warnings = payload.get('warnings', [])
        return jsonify({'status': 'success'}), 200
    
    # Preparing sensor data
    moisture_str = format(float(moisture), '.5f') if moisture is not None and moisture.replace('.', '', 1).isdigit() else None
    temp_str = format(float(temp), '.2f') if temp is not None and temp.replace('.', '', 1).isdigit() else None
    humidity_str = format(float(humidity), '.2f') if humidity is not None and humidity.replace('.', '', 1).isdigit() else None
    light_str = format(float(light), '.2f') if light is not None and light.replace('.', '', 1).isdigit() else None
    data_dict = {
        'moisture': moisture_str,
        'temp': temp_str,
        'humidity': humidity_str,
        'light': light_str,
        'warnings': warnings,
    }
    return render_template('My-Stats.html', data=data_dict)  # Pass data to template


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['photo']
    filename = 'static/images/most_recent_photo.jpg'
    file.save(filename)
    return 'Image uploaded successfully'

@app.route('/recent_photo', methods=['GET'])
def recent_photo():
    photos_folder = 'static/images/'
    files = os.listdir(photos_folder)
    files.sort(reverse=True)  # Sort files in descending order by name
    if files:
        recent_photo = files[0]
        return recent_photo
    return 'No recent photo available'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

