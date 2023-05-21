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
    
    # Parse the data (assumes it's a JSON string that represents a dictionary)
    data_dict = json.loads(data)
    global moisture, temp, humidity, light
    moisture = data_dict.get('moisture')
    temp = data_dict.get('temp')
    humidity = data_dict.get('humidity')
    light = data_dict.get('light')
    return jsonify({'status': 'success'}), 200


@app.route('/', methods=['GET', 'POST']) 
def index():
    if request.method == 'POST':
        global moisture, temp, humidity
        data = json.loads(request.data)
        moisture = data.get('moisture')
        temp = data.get('temp')
        humidity = data.get('humidity')

        print("Data types:")
        print("moisture:", type(moisture))
        print("temp:", type(temp))
        print("humidity:", type(humidity))

        print("Data availability:")
        print("moisture:", moisture)
        print("temp:", temp)
        print("humidity:", humidity)

        return jsonify({'status': 'success'}), 200
    
    moisture_str = format(moisture, '.5f') if moisture is not None else None
    temp_str = format(temp, '.2f') if temp is not None else None
    humidity_str = format(humidity, '.2f') if humidity is not None else None

    
    return render_template('index.html', moisture=moisture_str, temp=temp_str, humidity=humidity_str)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        global moisture, temp, humidity
        data = json.loads(request.data)
        moisture = data.get('moisture')
        temp = data.get('temp')
        humidity = data.get('humidity')

        return jsonify({'status': 'success'}), 200

    moisture_str = format(moisture, '.5f') if moisture is not None else None
    temp_str = format(temp, '.2f') if temp is not None else None
    humidity_str = format(humidity, '.2f') if humidity is not None else None

    return render_template('Home.html', moisture=moisture_str, temp=temp_str, humidity=humidity_str)

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    global moisture, temp, humidity, light, warnings
    if request.method == 'POST':
        payload = request.get_json()
        data = payload.get('data', {})
        warnings = payload.get('warnings', [])
        moisture = data.get('moisture')
        temp = data.get('temp')
        humidity = data.get('humidity')
        light = data.get('light')

        return jsonify({'status': 'success'}), 200
    
    moisture_str = format(moisture, '.5f') if moisture is not None else None
    temp_str = format(temp, '.2f') if temp is not None else None
    humidity_str = format(humidity, '.2f') if humidity is not None else None
    light_str = format(light, '.2f') if light is not None else None
    
    return render_template('My-Stats.html', moisture=moisture_str, temp=temp_str, humidity=humidity_str, light=light_str, warnings=warnings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

