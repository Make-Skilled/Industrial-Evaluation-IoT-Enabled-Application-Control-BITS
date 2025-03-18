# import requests
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# import pickle
# import numpy as np

# # ThingSpeak configuration
# CHANNEL_ID = "2225368"
# READ_API_KEY = "MT73TRXN6WQ5OJUC"
# BASE_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"

# def collect_thingspeak_data(results=1000):
#     """Collect data from ThingSpeak"""
#     params = {
#         'api_key': READ_API_KEY,
#         'results': results  # Get last 1000 entries
#     }
    
#     try:
#         response = requests.get(BASE_URL, params=params)
#         data = response.json()
        
#         if 'feeds' not in data:
#             raise Exception("No feeds found in ThingSpeak response")
            
#         # Convert feeds to DataFrame
#         df = pd.DataFrame(data['feeds'])
        
#         # Convert fields to numeric
#         for i in range(1, 7):  # fields 1-6
#             df[f'field{i}'] = pd.to_numeric(df[f'field{i}'], errors='coerce')
            
#         # Rename columns for clarity
#         df = df.rename(columns={
#             'field1': 'dht_temp',
#             'field2': 'humidity',
#             'field3': 'mlx_temp',
#             'field4': 'pressure',
#             'field5': 'bmp_temp',
#             'field6': 'mq135_value'
#         })
        
#         return df
        
#     except Exception as e:
#         print(f"Error collecting data: {str(e)}")
#         return None

# def create_failure_predictions(df):
#     """Create failure predictions based on sensor data"""
    
#     # Define thresholds for failure conditions
#     temp_threshold = 30.0
#     humidity_threshold = 70.0
#     pressure_threshold = 101325  # standard atmospheric pressure
#     air_quality_threshold = 1000
    
#     # Create failure conditions
#     df['failure'] = 0
    
#     # Set failure = 1 if any condition is met
#     conditions = [
#         (df['dht_temp'] > temp_threshold) | (df['mlx_temp'] > temp_threshold),
#         (df['humidity'] > humidity_threshold),
#         (df['pressure'] < pressure_threshold * 0.95) | (df['pressure'] > pressure_threshold * 1.05),
#         (df['mq135_value'] > air_quality_threshold)
#     ]
    
#     df.loc[np.any(conditions, axis=0), 'failure'] = 1
    
#     return df

# def train_model(df):
#     """Train a machine learning model"""
    
#     # Select features
#     features = ['dht_temp', 'humidity', 'mlx_temp', 'pressure', 'bmp_temp', 'mq135_value']
#     X = df[features]
#     y = df['failure']
    
#     # Split data
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
#     # Train model
#     model = RandomForestClassifier(n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)
    
#     # Print model accuracy
#     train_accuracy = model.score(X_train, y_train)
#     test_accuracy = model.score(X_test, y_test)
#     print(f"Train accuracy: {train_accuracy:.2f}")
#     print(f"Test accuracy: {test_accuracy:.2f}")
    
#     return model

# def main():
#     # Collect data
#     print("Collecting data from ThingSpeak...")
#     df = collect_thingspeak_data()
    
#     if df is None:
#         return
    
#     # Create failure predictions
#     print("Creating failure predictions...")
#     df = create_failure_predictions(df)
    
#     # Train model
#     print("Training model...")
#     model = train_model(df)
    
#     # Save model
#     print("Saving model...")
#     with open('model.pkl', 'wb') as f:
#         pickle.dump(model, f)
    
#     print("Model saved as model.pkl")

# if __name__ == "__main__":
#     main()