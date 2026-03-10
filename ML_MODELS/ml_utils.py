"""
Utility functions for ML models
Helper functions for data processing and visualization
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os

def create_sequence_from_tracking(object_history, sequence_length=10):
    """
    Create input sequence from tracking history
    
    Args:
        object_history: List of object states
        sequence_length: Desired sequence length
    
    Returns:
        Formatted sequence ready for model input
    """
    if len(object_history) < sequence_length:
        return None
    
    # Take most recent points
    recent = object_history[-sequence_length:]
    
    sequence = []
    for point in recent:
        features = [
            point.get('x', 0),
            point.get('y', 0),
            point.get('vx', 0),
            point.get('vy', 0),
            point.get('sensor1', 0),
            point.get('sensor2', 0),
            point.get('sensor3', 0),
            point.get('threat_score', 0)
        ]
        sequence.append(features)
    
    return np.array(sequence)

def compare_predictions(true_positions, predicted_positions):
    """
    Compare true vs predicted trajectories
    
    Args:
        true_positions: Actual positions
        predicted_positions: Predicted positions
    
    Returns:
        Error metrics
    """
    true_array = np.array(true_positions)
    pred_array = np.array(predicted_positions)
    
    # Calculate errors
    errors = np.sqrt(np.sum((true_array - pred_array)**2, axis=1))
    
    return {
        'mean_error': float(np.mean(errors)),
        'max_error': float(np.max(errors)),
        'min_error': float(np.min(errors)),
        'errors': errors.tolist()
    }

def plot_trajectory_comparison(true_traj, pred_traj, save_path=None):
    """
    Plot true vs predicted trajectory
    
    Args:
        true_traj: List of true positions
        pred_traj: List of predicted positions
        save_path: Optional path to save plot
    """
    plt.figure(figsize=(10, 8))
    
    true_array = np.array(true_traj)
    pred_array = np.array(pred_traj)
    
    # Plot trajectories
    plt.plot(true_array[:, 0], true_array[:, 1], 'b-', label='True', linewidth=2)
    plt.plot(pred_array[:, 0], pred_array[:, 1], 'r--', label='Predicted', linewidth=2)
    
    # Mark start and end
    plt.plot(true_array[0, 0], true_array[0, 1], 'go', markersize=10, label='Start')
    plt.plot(true_array[-1, 0], true_array[-1, 1], 'ro', markersize=10, label='End')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('X Position (cm)')
    plt.ylabel('Y Position (cm)')
    plt.title('Trajectory Prediction Comparison')
    plt.legend()
    plt.axis('equal')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def export_predictions_to_json(predictions, filename=None):
    """
    Export predictions to JSON file
    
    Args:
        predictions: Prediction results
        filename: Output filename
    """
    if filename is None:
        filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Ensure directory exists
    os.makedirs('DATA/predictions', exist_ok=True)
    filepath = os.path.join('DATA/predictions', filename)
    
    with open(filepath, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions
        }, f, indent=2)
    
    print(f"✅ Predictions saved to {filepath}")
    return filepath

def calculate_prediction_accuracy(predictions, ground_truth, threshold=10):
    """
    Calculate prediction accuracy within threshold
    
    Args:
        predictions: Predicted positions
        ground_truth: Actual positions
        threshold: Acceptable error threshold (cm)
    
    Returns:
        Accuracy metrics
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground truth must have same length")
    
    errors = []
    correct = 0
    
    for pred, truth in zip(predictions, ground_truth):
        error = np.sqrt((pred['x'] - truth[0])**2 + (pred['y'] - truth[1])**2)
        errors.append(error)
        if error <= threshold:
            correct += 1
    
    accuracy = correct / len(predictions) * 100
    
    return {
        'accuracy': accuracy,
        'mean_error': np.mean(errors),
        'std_error': np.std(errors),
        'errors': errors
    }