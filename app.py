from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Global variables to hold the sensor data
moisture = None
temp = None
humidity = None
light = None
warnings = []



@app.route('/particle', methods=['POST'])
def particle():
    data = request.json['data']
    print('Data received from Particle:', data)
    data_dict = json.loads(data)
    global moisture, temp, humidity, light
    moisture = data_dict.get('moisture')
    temp = data_dict.get('temp')
    humidity = data_dict.get('humidity')
    light = data_dict.get('light')
    return jsonify({'status': 'success'}), 200

@app.route('/data', methods=['GET'])
def data():
    moisture_str = format(moisture, '.5f') if moisture is not None else None
    temp_str = format(temp, '.2f') if temp is not None else None
    humidity_str = format(humidity, '.2f') if humidity is not None else None
    light_str = format(light, '.2f') if light is not None else None

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
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    global warnings
    if request.method == 'POST':
        payload = request.get_json()
        warnings = payload.get('warnings', [])
        return jsonify({'status': 'success'}), 200
    return render_template('My-Stats.html', warnings=warnings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

