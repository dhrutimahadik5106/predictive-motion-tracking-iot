"""
Model Trainer for Trajectory Prediction
Trains LSTM models on collected trajectory data
"""

import numpy as np
import json
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
from trajectory_predictor import TrajectoryPredictor
from data_collector import DataCollector

class ModelTrainer:
    """
    Handles training of trajectory prediction models
    """
    
    def __init__(self, data_dir='DATA/training', model_dir='ML_MODELS'):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.predictor = TrajectoryPredictor()
        self.collector = DataCollector()
        
    def load_training_data(self, data_files=None):
        """
        Load and combine training data from multiple files
        
        Args:
            data_files: List of data files to load (None = all)
        """
        if data_files is None:
            # Load all JSON files in data_dir
            data_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        
        X_list = []
        y_list = []
        
        for file in data_files:
            file_path = os.path.join(self.data_dir, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract sequences
            for seq in data['sequences']:
                # Process input sequence
                input_seq = []
                for frame in seq['input']:
                    features = []
                    for feat in self.predictor.config['features']:
                        features.append(frame.get(feat, 0))
                    input_seq.append(features)
                
                # Process target sequence
                target_seq = []
                for frame in seq['target']:
                    target_seq.append([frame['x'], frame['y']])
                
                X_list.append(input_seq)
                y_list.append(target_seq)
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"✅ Loaded {len(X)} sequences")
        print(f"Input shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        return X, y
    
    def preprocess_data(self, X, y):
        """
        Normalize features and prepare for training
        """
        # Reshape for scaling
        original_X_shape = X.shape
        X_flat = X.reshape(-1, X.shape[-1])
        
        # Fit scaler
        scaler = StandardScaler()
        X_normalized = scaler.fit_transform(X_flat)
        
        # Reshape back
        X_normalized = X_normalized.reshape(original_X_shape)
        
        # Store scaler in predictor
        self.predictor.scaler = scaler
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=0.2, random_state=42
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        print(f"Training set: {X_train.shape}")
        print(f"Validation set: {X_val.shape}")
        print(f"Test set: {X_test.shape}")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
    
    def train(self, data_files=None, epochs=None):
        """
        Train model on collected data
        
        Args:
            data_files: Specific data files to use
            epochs: Number of training epochs
        """
        # Load data
        X, y = self.load_training_data(data_files)
        
        if len(X) == 0:
            print("❌ No training data found")
            return
        
        # Preprocess
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = self.preprocess_data(X, y)
        
        # Update epochs if specified
        if epochs:
            self.predictor.config['epochs'] = epochs
        
        # Train model
        history = self.predictor.train(X_train, y_train, X_val, y_val)
        
        # Evaluate on test set
        test_loss = self.predictor.model.evaluate(
            X_test, y_test.reshape(y_test.shape[0], -1),
            verbose=0
        )
        print(f"✅ Test loss: {test_loss}")
        
        # Save model
        self.predictor.save_model()
        
        return history
    
    def evaluate_on_live_data(self, num_samples=100):
        """
        Evaluate model on live/collected data
        """
        X, y = self.load_training_data()
        
        if len(X) == 0:
            print("❌ No data for evaluation")
            return
        
        # Use last num_samples for evaluation
        X_eval = X[-num_samples:]
        y_eval = y[-num_samples:]
        
        # Normalize using existing scaler
        if self.predictor.scaler:
            original_shape = X_eval.shape
            X_flat = X_eval.reshape(-1, X_eval.shape[-1])
            X_norm = self.predictor.scaler.transform(X_flat)
            X_eval = X_norm.reshape(original_shape)
        
        # Predict
        y_pred_flat = self.predictor.model.predict(X_eval, verbose=0)
        y_pred = y_pred_flat.reshape(y_pred_flat.shape[0], -1, 2)
        
        # Calculate metrics
        errors = []
        for i in range(len(y_pred)):
            for j in range(y_pred.shape[1]):
                true_pos = y_eval[i, j]
                pred_pos = y_pred[i, j]
                error = np.sqrt((true_pos[0] - pred_pos[0])**2 + 
                               (true_pos[1] - pred_pos[1])**2)
                errors.append(error)
        
        errors = np.array(errors)
        
        results = {
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'max_error': float(np.max(errors)),
            'min_error': float(np.min(errors)),
            'error_percentiles': {
                '25%': float(np.percentile(errors, 25)),
                '50%': float(np.percentile(errors, 50)),
                '75%': float(np.percentile(errors, 75)),
                '90%': float(np.percentile(errors, 90))
            }
        }
        
        print("\n📊 Evaluation Results:")
        print(f"Mean Error: {results['mean_error']:.2f} cm")
        print(f"Std Error: {results['std_error']:.2f} cm")
        print(f"90th Percentile: {results['error_percentiles']['90%']:.2f} cm")
        
        return results

# Example usage
if __name__ == "__main__":
    trainer = ModelTrainer()
    
    # Train model
    trainer.train(epochs=50)
    
    # Evaluate
    trainer.evaluate_on_live_data()