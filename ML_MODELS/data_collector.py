"""
Data Collector for Training ML Models
Collects real-time tracking data for training trajectory prediction models
"""

import json
import csv
import numpy as np
from datetime import datetime
from collections import deque
import os

class DataCollector:
    """
    Collects and preprocesses trajectory data for ML training
    
    Features collected:
    - Position (x, y) over time
    - Velocity (vx, vy)
    - Acceleration
    - Sensor readings
    - Threat levels
    - Object type/behavior
    """
    
    def __init__(self, config_file='DATA/model_config.json'):
        self.config = self.load_config(config_file)
        self.trajectory_buffer = deque(maxlen=1000)
        self.training_data = []
        self.labels = []
        self.collection_active = False
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create data directory if not exists
        os.makedirs('DATA/training', exist_ok=True)
        os.makedirs('DATA/raw', exist_ok=True)
        
    def load_config(self, config_file):
        """Load configuration from JSON"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                'sequence_length': 10,      # Number of time steps for LSTM
                'prediction_horizon': 5,     # Steps to predict ahead
                'features': [
                    'x', 'y', 'vx', 'vy', 
                    'sensor1', 'sensor2', 'sensor3',
                    'threat_score'
                ],
                'sampling_rate': 5,          # Hz
                'min_trajectory_length': 20
            }
    
    def start_collection(self):
        """Start data collection"""
        self.collection_active = True
        self.trajectory_buffer.clear()
        print(f"📊 Data collection started - Session: {self.session_id}")
        
    def stop_collection(self):
        """Stop data collection and save"""
        self.collection_active = False
        self.save_collected_data()
        print(f"💾 Data saved - Total trajectories: {len(self.training_data)}")
        
    def add_frame(self, objects, timestamp=None):
        """
        Add a single frame of tracking data
        
        Args:
            objects: List of tracked objects
            timestamp: Optional timestamp
        """
        if not self.collection_active:
            return
            
        if timestamp is None:
            timestamp = datetime.now().timestamp()
            
        # Process each object
        for obj in objects:
            frame_data = {
                'timestamp': timestamp,
                'object_id': obj['id'],
                'x': obj['x'],
                'y': obj['y'],
                'vx': obj.get('vx', 0),
                'vy': obj.get('vy', 0),
                'sensor1': obj.get('sensor1', 0),
                'sensor2': obj.get('sensor2', 0),
                'sensor3': obj.get('sensor3', 0),
                'threat_score': obj.get('threatScore', 0),
                'threat_level': obj.get('threatLevel', 'LOW'),
                'behavior': obj.get('behavior', 'unknown')
            }
            
            self.trajectory_buffer.append(frame_data)
            
        # Extract sequences for training
        self.extract_training_sequences()
        
    def extract_training_sequences(self):
        """Extract sequences from trajectory buffer for training"""
        if len(self.trajectory_buffer) < self.config['sequence_length'] + self.config['prediction_horizon']:
            return
            
        # Group by object_id
        object_sequences = {}
        
        for frame in self.trajectory_buffer:
            obj_id = frame['object_id']
            if obj_id not in object_sequences:
                object_sequences[obj_id] = []
            object_sequences[obj_id].append(frame)
            
        # Extract sequences for each object
        for obj_id, sequence in object_sequences.items():
            if len(sequence) >= self.config['sequence_length'] + self.config['prediction_horizon']:
                # Create sliding windows
                for i in range(len(sequence) - self.config['sequence_length'] - self.config['prediction_horizon'] + 1):
                    input_seq = sequence[i:i + self.config['sequence_length']]
                    target_seq = sequence[i + self.config['sequence_length']:
                                         i + self.config['sequence_length'] + self.config['prediction_horizon']]
                    
                    self.training_data.append({
                        'input': input_seq,
                        'target': target_seq,
                        'object_id': obj_id,
                        'timestamp': sequence[i]['timestamp']
                    })
    
    def prepare_training_data(self):
        """
        Prepare data for model training
        
        Returns:
            X: Input sequences (samples, sequence_length, features)
            y: Target sequences (samples, prediction_horizon, 2)  # x, y positions
        """
        X = []
        y = []
        
        feature_indices = {f: i for i, f in enumerate(self.config['features'])}
        
        for data in self.training_data:
            # Create input sequence
            input_sequence = []
            for frame in data['input']:
                feature_vector = []
                for feature in self.config['features']:
                    feature_vector.append(frame.get(feature, 0))
                input_sequence.append(feature_vector)
            
            # Create target sequence (x, y positions)
            target_sequence = []
            for frame in data['target']:
                target_sequence.append([frame['x'], frame['y']])
            
            X.append(input_sequence)
            y.append(target_sequence)
        
        return np.array(X), np.array(y)
    
    def save_collected_data(self):
        """Save collected data to CSV and JSON"""
        # Save raw data
        raw_file = f"DATA/raw/raw_data_{self.session_id}.csv"
        with open(raw_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['timestamp', 'object_id', 'x', 'y', 'vx', 'vy', 
                           'sensor1', 'sensor2', 'sensor3', 'threat_score', 
                           'threat_level', 'behavior'])
            
            for frame in self.trajectory_buffer:
                writer.writerow([
                    frame['timestamp'], frame['object_id'], frame['x'], frame['y'],
                    frame['vx'], frame['vy'], frame['sensor1'], frame['sensor2'],
                    frame['sensor3'], frame['threat_score'], frame['threat_level'],
                    frame['behavior']
                ])
        
        # Save training sequences
        training_file = f"DATA/training/training_data_{self.session_id}.json"
        with open(training_file, 'w') as f:
            json.dump({
                'config': self.config,
                'sequences': self.training_data,
                'num_sequences': len(self.training_data)
            }, f, indent=2)
        
        print(f"✅ Data saved to {raw_file} and {training_file}")
        
    def get_statistics(self):
        """Get collection statistics"""
        return {
            'total_frames': len(self.trajectory_buffer),
            'training_sequences': len(self.training_data),
            'unique_objects': len(set(f['object_id'] for f in self.trajectory_buffer)),
            'duration': self.get_collection_duration(),
            'features': self.config['features']
        }
    
    def get_collection_duration(self):
        """Calculate collection duration in seconds"""
        if len(self.trajectory_buffer) < 2:
            return 0
        timestamps = [f['timestamp'] for f in self.trajectory_buffer]
        return max(timestamps) - min(timestamps)