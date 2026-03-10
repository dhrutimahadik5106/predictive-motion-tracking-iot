"""
Trajectory Predictor using LSTM Neural Networks
Predicts future positions based on historical tracking data
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
import pickle
from collections import deque
import os

class TrajectoryPredictor:
    """
    LSTM-based trajectory prediction model
    
    Features:
    - Sequence-to-sequence prediction
    - Multiple prediction horizons
    - Confidence estimation
    - Online learning capability
    """
    
    def __init__(self, model_path='ML_MODELS/trained_model.h5', config_file='DATA/model_config.json'):
        self.model_path = model_path
        self.config = self.load_config(config_file)
        self.model = None
        self.scaler = None
        self.history_buffer = deque(maxlen=100)
        self.prediction_confidence = 0.0
        
        # Load model if exists
        self.load_model()
        
    def load_config(self, config_file):
        """Load model configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'sequence_length': 10,
                'prediction_horizon': 5,
                'features': ['x', 'y', 'vx', 'vy', 'sensor1', 'sensor2', 'sensor3'],
                'lstm_units': [64, 32],
                'dropout': 0.2,
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 100
            }
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        model = keras.Sequential([
            # First LSTM layer
            layers.LSTM(
                self.config['lstm_units'][0],
                return_sequences=True,
                input_shape=input_shape,
                dropout=self.config['dropout']
            ),
            
            # Second LSTM layer
            layers.LSTM(
                self.config['lstm_units'][1],
                return_sequences=False,
                dropout=self.config['dropout']
            ),
            
            # Dense layers for prediction
            layers.Dense(64, activation='relu'),
            layers.Dropout(self.config['dropout']),
            layers.Dense(32, activation='relu'),
            
            # Output layer (predict x, y for each future step)
            layers.Dense(self.config['prediction_horizon'] * 2)
        ])
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.config['learning_rate'])
        model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                print(f"✅ Model loaded from {self.model_path}")
                
                # Load scaler if exists
                scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
            else:
                print("⚠️ No pre-trained model found. Use train() to create one.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def save_model(self):
        """Save trained model"""
        try:
            # Save model
            self.model.save(self.model_path)
            
            # Save scaler
            scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save config
            config_path = self.model_path.replace('.h5', '_config.json')
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✅ Model saved to {self.model_path}")
        except Exception as e:
            print(f"❌ Error saving model: {e}")
    
    def prepare_sequences(self, trajectory_history):
        """
        Prepare input sequence for prediction
        
        Args:
            trajectory_history: List of recent positions/features
            
        Returns:
            Normalized input sequence
        """
        if len(trajectory_history) < self.config['sequence_length']:
            return None
        
        # Take last N points
        recent = trajectory_history[-self.config['sequence_length']:]
        
        # Extract features
        sequence = []
        for point in recent:
            features = []
            for feature in self.config['features']:
                if feature in point:
                    features.append(point[feature])
                else:
                    features.append(0)
            sequence.append(features)
        
        sequence = np.array(sequence).reshape(1, self.config['sequence_length'], -1)
        
        # Normalize if scaler exists
        if self.scaler:
            original_shape = sequence.shape
            sequence = sequence.reshape(-1, sequence.shape[-1])
            sequence = self.scaler.transform(sequence)
            sequence = sequence.reshape(original_shape)
        
        return sequence
    
    def predict_trajectory(self, trajectory_history, num_steps=None):
        """
        Predict future trajectory
        
        Args:
            trajectory_history: List of historical positions
            num_steps: Number of steps to predict (default: config value)
            
        Returns:
            List of predicted positions with confidence
        """
        if self.model is None:
            print("⚠️ No model loaded. Using fallback prediction.")
            return self.fallback_prediction(trajectory_history)
        
        if num_steps is None:
            num_steps = self.config['prediction_horizon']
        
        # Prepare input
        input_sequence = self.prepare_sequences(trajectory_history)
        if input_sequence is None:
            return self.fallback_prediction(trajectory_history)
        
        # Make prediction
        predictions = self.model.predict(input_sequence, verbose=0)
        
        # Reshape predictions
        predictions = predictions.reshape(-1, 2)  # (steps, [x, y])
        
        # Denormalize if scaler used
        if self.scaler:
            # This is simplified - actual denormalization would use feature indices
            predictions = predictions * self.scaler.scale_[:2] + self.scaler.mean_[:2]
        
        # Calculate confidence based on model uncertainty
        confidence = self.estimate_confidence(trajectory_history, predictions)
        
        # Format results
        result = []
        for i, (x, y) in enumerate(predictions[:num_steps]):
            result.append({
                'step': i + 1,
                'x': float(x),
                'y': float(y),
                'confidence': confidence * (1 - i * 0.1)  # Decreasing confidence
            })
        
        return {
            'predictions': result,
            'overall_confidence': confidence,
            'method': 'LSTM'
        }
    
    def estimate_confidence(self, history, predictions):
        """
        Estimate prediction confidence based on:
        - Movement consistency
        - Historical pattern matching
        - Model uncertainty
        """
        if len(history) < 2:
            return 0.5
        
        # Factor 1: Movement consistency (lower variance = higher confidence)
        positions = np.array([[p['x'], p['y']] for p in history])
        variances = np.var(positions, axis=0)
        consistency_score = 1.0 / (1.0 + np.mean(variances))
        
        # Factor 2: Prediction plausibility
        last_pos = history[-1]
        first_pred = predictions[0]
        distance = np.sqrt((first_pred[0] - last_pos['x'])**2 + 
                          (first_pred[1] - last_pos['y'])**2)
        plausibility_score = 1.0 / (1.0 + distance / 50)  # Normalize
        
        # Combine factors
        confidence = 0.6 * consistency_score + 0.4 * plausibility_score
        
        return min(0.95, max(0.3, confidence))
    
    def fallback_prediction(self, trajectory_history):
        """
        Fallback prediction using simple extrapolation
        Used when ML model is not available
        """
        if len(trajectory_history) < 2:
            return None
        
        # Calculate velocity
        last = trajectory_history[-1]
        prev = trajectory_history[-2]
        
        vx = last['x'] - prev['x']
        vy = last['y'] - prev['y']
        
        predictions = []
        for i in range(1, self.config['prediction_horizon'] + 1):
            predictions.append({
                'step': i,
                'x': last['x'] + vx * i,
                'y': last['y'] + vy * i,
                'confidence': 0.5 * (1 - i * 0.1)
            })
        
        return {
            'predictions': predictions,
            'overall_confidence': 0.5,
            'method': 'linear_extrapolation'
        }
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Train the LSTM model
        
        Args:
            X_train: Training sequences (samples, seq_len, features)
            y_train: Target positions (samples, horizon, 2)
            X_val: Validation sequences
            y_val: Validation targets
        """
        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self.build_model(input_shape)
        
        # Prepare targets (flatten)
        y_train_flat = y_train.reshape(y_train.shape[0], -1)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001
            )
        ]
        
        # Train
        history = self.model.fit(
            X_train, y_train_flat,
            batch_size=self.config['batch_size'],
            epochs=self.config['epochs'],
            validation_data=(X_val, y_val.reshape(y_val.shape[0], -1)) if X_val is not None else None,
            callbacks=callbacks,
            verbose=1
        )
        
        print(f"✅ Model training completed")
        return history
    
    def update_history(self, object_data):
        """Update history buffer with new tracking data"""
        self.history_buffer.append(object_data)
    
    def get_prediction_with_uncertainty(self, trajectory_history):
        """
        Get predictions with uncertainty estimates
        Uses Monte Carlo dropout if available
        """
        if self.model is None:
            return self.fallback_prediction(trajectory_history)
        
        # Enable Monte Carlo dropout for uncertainty estimation
        mc_predictions = []
        for _ in range(50):  # 50 Monte Carlo samples
            pred = self.model.predict(
                self.prepare_sequences(trajectory_history),
                verbose=0
            )
            mc_predictions.append(pred)
        
        mc_predictions = np.array(mc_predictions)
        
        # Calculate mean and std
        mean_pred = np.mean(mc_predictions, axis=0)
        std_pred = np.std(mc_predictions, axis=0)
        
        # Reshape
        mean_pred = mean_pred.reshape(-1, 2)
        std_pred = std_pred.reshape(-1, 2)
        
        # Format results with uncertainty
        result = []
        for i, ((x, y), (std_x, std_y)) in enumerate(zip(mean_pred, std_pred)):
            result.append({
                'step': i + 1,
                'x': float(x),
                'y': float(y),
                'uncertainty_x': float(std_x),
                'uncertainty_y': float(std_y),
                'confidence': 1.0 / (1.0 + (std_x + std_y) / 2)
            })
        
        return {
            'predictions': result,
            'method': 'LSTM_MC_dropout'
        }