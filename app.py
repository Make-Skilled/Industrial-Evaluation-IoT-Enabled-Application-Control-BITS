from flask import Flask, render_template, jsonify, request
import requests
import json

app = Flask(__name__)

# ThingSpeak configuration
CHANNEL_ID = "2225368"
READ_API_KEY = "MT73TRXN6WQ5OJUC"
WRITE_API_KEY = "VUX286JN0ZVGAPGQ"  # Add your write API key here
BASE_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
WRITE_URL = f"https://api.thingspeak.com/update"

OUTPUT_CHANNEL_ID = "2271034"
OUTPUT_READ_API_KEY = "QJ8K34Q6S37OZQD0"
OUTPUT_WRITE_API_KEY = "1K948MMGSN37H3HE"  

@app.route('/')
def dashboard():
    # Fetch data from ThingSpeak
    params = {
        'api_key': READ_API_KEY,
        'results': 20  # Get last 20 entries for historical data
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'feeds' in data and len(data['feeds']) > 0:
            latest_feed = data['feeds'][0]
            sensor_data = {
                'dht_temp': latest_feed['field1'],
                'humidity': latest_feed['field2'],
                'mlx_temp': latest_feed['field3'],
                'pressure': latest_feed['field4'],
                'bmp_temp': latest_feed['field5'],
                'mq135_value': latest_feed['field6'],
                'fan_status': latest_feed['field7']
            }
            
            # Prepare historical data
            historical_data = {
                'labels': [feed['created_at'].split('T')[1].split('Z')[0] for feed in reversed(data['feeds'])],
                'dht_temp': [feed['field1'] for feed in reversed(data['feeds'])],
                'humidity': [feed['field2'] for feed in reversed(data['feeds'])],
                'mlx_temp': [feed['field3'] for feed in reversed(data['feeds'])],
                'pressure': [feed['field4'] for feed in reversed(data['feeds'])],
                'bmp_temp': [feed['field5'] for feed in reversed(data['feeds'])],
                'mq135_value': [feed['field6'] for feed in reversed(data['feeds'])]
            }
            
            return render_template('dashboard.html', sensor_data=sensor_data, historical_data=historical_data)
        else:
            return render_template('dashboard.html', sensor_data=None, historical_data=None)
    
    except Exception as e:
        return f"Error fetching data: {str(e)}"

@app.route('/toggle_control', methods=['POST'])
def toggle_control():
    try:
        # Get the state from request body (true/false)
        state = request.json.get('state', False)
        
        # Convert boolean to integer (true -> 1, false -> 2)
        value = 1 if state else 2
        
        print(f"Received state: {state}, Sending value to ThingSpeak: {value}")  # Debug print
        
        # Send data to ThingSpeak
        params = {
            'api_key': OUTPUT_WRITE_API_KEY,
            'field1': value
        }
        
        response = requests.get(WRITE_URL, params=params)
        if response.status_code == 200:
            # Return the actual state that was sent to ThingSpeak
            return jsonify({'success': True, 'state': state, 'value': value})
        else:
            return jsonify({'success': False, 'error': 'Failed to update ThingSpeak'}), 400
            
    except Exception as e:
        print(f"Error in toggle_control: {str(e)}")  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
