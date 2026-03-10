"""
Kalman Filter Output Demonstration
Shows all the data the Kalman filter produces
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import json

class KalmanOutputVisualizer:
    """
    Demonstrates all outputs from the Kalman filter
    """
    
    def __init__(self):
        self.kalman_data = {
            'filtered_states': [],      # Smoothed positions
            'raw_measurements': [],      # Raw sensor data
            'velocities': [],            # Estimated velocities
            'accelerations': [],          # Estimated accelerations
            'uncertainties': [],          # Covariance traces
            'predictions': [],            # Future predictions
            'innovation': [],             # Measurement residuals
            'gain': []                     # Kalman gain history
        }
        
    def generate_sample_kalman_output(self):
        """Generate sample data showing all Kalman outputs"""
        
        # Simulate 100 time steps
        for t in range(100):
            # True position (sine wave with noise)
            true_x = 50 + 30 * np.sin(t * 0.1)
            true_y = 50 + 20 * np.cos(t * 0.12)
            
            # Raw measurement (with noise)
            measured_x = true_x + np.random.normal(0, 2)
            measured_y = true_y + np.random.normal(0, 2)
            
            # Kalman filtered state (smoothed)
            filtered_x = true_x + np.random.normal(0, 0.5)  # Less noise
            filtered_y = true_y + np.random.normal(0, 0.5)
            
            # Calculate velocities
            if t > 0:
                vx = filtered_x - self.kalman_data['filtered_states'][-1]['x']
                vy = filtered_y - self.kalman_data['filtered_states'][-1]['y']
            else:
                vx, vy = 0, 0
            
            # Calculate accelerations
            if t > 1:
                prev_vx = self.kalman_data['velocities'][-1]['vx']
                prev_vy = self.kalman_data['velocities'][-1]['vy']
                ax = vx - prev_vx
                ay = vy - prev_vy
            else:
                ax, ay = 0, 0
            
            # Uncertainty (decreases over time as filter converges)
            uncertainty = 5.0 * np.exp(-t/20) + 0.5
            
            # Kalman gain (how much to trust measurement vs prediction)
            kalman_gain = 1.0 - uncertainty/5.0
            
            # Innovation (difference between measurement and prediction)
            innovation_x = measured_x - filtered_x
            innovation_y = measured_y - filtered_y
            
            # Store filtered state
            self.kalman_data['filtered_states'].append({
                'x': filtered_x,
                'y': filtered_y,
                'timestamp': t
            })
            
            # Store raw measurement
            self.kalman_data['raw_measurements'].append({
                'x': measured_x,
                'y': measured_y,
                'timestamp': t
            })
            
            # Store velocity
            self.kalman_data['velocities'].append({
                'vx': vx,
                'vy': vy,
                'speed': np.sqrt(vx**2 + vy**2),
                'timestamp': t
            })
            
            # Store acceleration
            self.kalman_data['accelerations'].append({
                'ax': ax,
                'ay': ay,
                'magnitude': np.sqrt(ax**2 + ay**2),
                'timestamp': t
            })
            
            # Store uncertainty
            self.kalman_data['uncertainties'].append({
                'value': uncertainty,
                'timestamp': t
            })
            
            # Store innovation
            self.kalman_data['innovation'].append({
                'x': innovation_x,
                'y': innovation_y,
                'magnitude': np.sqrt(innovation_x**2 + innovation_y**2),
                'timestamp': t
            })
            
            # Store Kalman gain
            self.kalman_data['gain'].append({
                'value': kalman_gain,
                'timestamp': t
            })
            
            # Generate predictions every 10 steps
            if t % 10 == 0:
                predictions = []
                for step in range(1, 6):
                    pred_x = filtered_x + vx * step
                    pred_y = filtered_y + vy * step
                    predictions.append({
                        'step': step,
                        'x': pred_x,
                        'y': pred_y,
                        'uncertainty': uncertainty * (1 + step * 0.2)
                    })
                self.kalman_data['predictions'].append({
                    'timestamp': t,
                    'predictions': predictions
                })
        
        return self.kalman_data
    
    def print_kalman_output_summary(self):
        """Print human-readable summary of Kalman outputs"""
        
        print("="*60)
        print("📊 KALMAN FILTER OUTPUT SUMMARY")
        print("="*60)
        
        # Latest state
        latest = self.kalman_data['filtered_states'][-1]
        latest_vel = self.kalman_data['velocities'][-1]
        latest_acc = self.kalman_data['accelerations'][-1]
        latest_uncertainty = self.kalman_data['uncertainties'][-1]
        
        print(f"\n📍 CURRENT STATE (Object #1):")
        print(f"   Position: ({latest['x']:.2f}, {latest['y']:.2f}) cm")
        print(f"   Velocity: ({latest_vel['vx']:.2f}, {latest_vel['vy']:.2f}) cm/s")
        print(f"   Speed: {latest_vel['speed']:.2f} cm/s")
        print(f"   Acceleration: ({latest_acc['ax']:.3f}, {latest_acc['ay']:.3f}) cm/s²")
        print(f"   Uncertainty: ±{latest_uncertainty['value']:.2f} cm")
        
        # Statistics
        uncertainties = [u['value'] for u in self.kalman_data['uncertainties']]
        innovations = [i['magnitude'] for i in self.kalman_data['innovation']]
        
        print(f"\n📈 FILTER STATISTICS:")
        print(f"   Avg Uncertainty: {np.mean(uncertainties):.2f} cm")
        print(f"   Min Uncertainty: {np.min(uncertainties):.2f} cm")
        print(f"   Max Uncertainty: {np.max(uncertainties):.2f} cm")
        print(f"   Avg Innovation: {np.mean(innovations):.2f} cm")
        print(f"   Filter Convergence: {(1 - np.mean(uncertainties)/5)*100:.1f}%")
        
        # Latest predictions
        latest_pred = self.kalman_data['predictions'][-1]
        print(f"\n🔮 FUTURE PREDICTIONS:")
        for pred in latest_pred['predictions']:
            print(f"   Step {pred['step']}: ({pred['x']:.1f}, {pred['y']:.1f}) "
                  f"±{pred['uncertainty']:.1f} cm")
        
        # Kalman gain
        latest_gain = self.kalman_data['gain'][-1]
        print(f"\n⚙️ KALMAN PARAMETERS:")
        print(f"   Kalman Gain: {latest_gain['value']:.3f}")
        print(f"   Measurement Trust: {latest_gain['value']*100:.1f}%")
        print(f"   Prediction Trust: {(1-latest_gain['value'])*100:.1f}%")
    
    def create_visualization_data(self):
        """Create JSON data for dashboard visualization"""
        
        visualization_data = {
            'current_state': {
                'position': self.kalman_data['filtered_states'][-1],
                'velocity': self.kalman_data['velocities'][-1],
                'acceleration': self.kalman_data['accelerations'][-1],
                'uncertainty': self.kalman_data['uncertainties'][-1]
            },
            'history': {
                'positions': [{'x': s['x'], 'y': s['y']} 
                             for s in self.kalman_data['filtered_states'][-50:]],
                'raw_measurements': [{'x': m['x'], 'y': m['y']} 
                                    for m in self.kalman_data['raw_measurements'][-50:]],
                'uncertainties': [u['value'] for u in self.kalman_data['uncertainties'][-50:]],
                'innovations': [i['magnitude'] for i in self.kalman_data['innovation'][-50:]],
                'kalman_gain': [g['value'] for g in self.kalman_data['gain'][-50:]]
            },
            'predictions': self.kalman_data['predictions'][-1]['predictions'],
            'statistics': {
                'avg_uncertainty': float(np.mean([u['value'] for u in self.kalman_data['uncertainties']])),
                'current_uncertainty': float(self.kalman_data['uncertainties'][-1]['value']),
                'avg_innovation': float(np.mean([i['magnitude'] for i in self.kalman_data['innovation']])),
                'filter_confidence': float(100 - np.mean([u['value'] for u in self.kalman_data['uncertainties']])*10)
            }
        }
        
        return visualization_data

# Run demonstration
if __name__ == "__main__":
    viz = KalmanOutputVisualizer()
    viz.generate_sample_kalman_output()
    viz.print_kalman_output_summary()
    
    # Save visualization data
    data = viz.create_visualization_data()
    with open('kalman_output.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\n✅ Kalman output saved to kalman_output.json")