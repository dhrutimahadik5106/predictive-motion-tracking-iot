"""
Kalman Filter for Smooth Object Tracking
Provides optimal state estimation with noise filtering
"""

import numpy as np
from filterpy.kalman import KalmanFilter
import json

class KalmanPredictor:
    """
    Kalman Filter-based tracking and prediction
    
    Features:
    - Smooth trajectory estimation
    - Noise filtering
    - Multi-step prediction
    - Uncertainty estimation
    """
    
    def __init__(self):
        self.trackers = {}  # object_id -> KalmanFilter
        self.object_states = {}
        self.next_id = 0
        
        # Kalman parameters
        self.dt = 0.1  # Time step
        self.position_std = 0.5  # Measurement noise
        self.acceleration_std = 0.2  # Process noise
        
    def create_kalman_filter(self, initial_position=None):
        """
        Create a new Kalman filter for tracking
        
        State vector: [x, y, vx, vy, ax, ay]
        Measurement: [x, y]
        """
        kf = KalmanFilter(dim_x=6, dim_z=2)
        
        # State transition matrix (constant acceleration model)
        kf.F = np.array([
            [1, 0, self.dt, 0, 0.5*self.dt**2, 0],
            [0, 1, 0, self.dt, 0, 0.5*self.dt**2],
            [0, 0, 1, 0, self.dt, 0],
            [0, 0, 0, 1, 0, self.dt],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]
        ])
        
        # Measurement matrix (we only measure position)
        kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0]
        ])
        
        # Measurement noise
        kf.R = np.array([
            [self.position_std**2, 0],
            [0, self.position_std**2]
        ])
        
        # Process noise
        q = self.acceleration_std**2
        kf.Q = np.array([
            [0.25*self.dt**4, 0, 0.5*self.dt**3, 0, 0.5*self.dt**2, 0],
            [0, 0.25*self.dt**4, 0, 0.5*self.dt**3, 0, 0.5*self.dt**2],
            [0.5*self.dt**3, 0, self.dt**2, 0, self.dt, 0],
            [0, 0.5*self.dt**3, 0, self.dt**2, 0, self.dt],
            [0.5*self.dt**2, 0, self.dt, 0, 1, 0],
            [0, 0.5*self.dt**2, 0, self.dt, 0, 1]
        ]) * q
        
        # Initial state covariance
        kf.P *= 1000
        
        if initial_position:
            kf.x = np.array([initial_position[0], initial_position[1], 0, 0, 0, 0])
        
        return kf
    
    def update(self, detections):
        """
        Update Kalman filters with new detections
        
        Args:
            detections: List of detected objects with 'id', 'x', 'y'
        
        Returns:
            List of tracked objects with smoothed states
        """
        tracked_objects = []
        
        # Match detections to existing trackers
        for detection in detections:
            obj_id = detection.get('id')
            x, y = detection['x'], detection['y']
            
            if obj_id in self.trackers:
                # Update existing tracker
                kf = self.trackers[obj_id]
                kf.predict()
                kf.update(np.array([x, y]))
            else:
                # Create new tracker
                kf = self.create_kalman_filter((x, y))
                self.trackers[obj_id] = kf
                self.object_states[obj_id] = {
                    'history': [],
                    'created': detection.get('timestamp', 0)
                }
            
            # Get current state
            state = kf.x
            covariance = kf.P
            
            # Calculate uncertainty (trace of position covariance)
            uncertainty = np.sqrt(np.trace(covariance[:2, :2]))
            
            # Store in object state
            obj_state = {
                'id': obj_id,
                'x': float(state[0]),
                'y': float(state[1]),
                'vx': float(state[2]),
                'vy': float(state[3]),
                'ax': float(state[4]),
                'ay': float(state[5]),
                'uncertainty': float(uncertainty),
                'timestamp': detection.get('timestamp', 0)
            }
            
            self.object_states[obj_id]['history'].append(obj_state)
            tracked_objects.append(obj_state)
        
        # Predict for objects without current detection
        for obj_id, kf in self.trackers.items():
            if obj_id not in [d.get('id') for d in detections]:
                kf.predict()
                
                # Get predicted state
                state = kf.x
                uncertainty = np.sqrt(np.trace(kf.P[:2, :2]))
                
                tracked_objects.append({
                    'id': obj_id,
                    'x': float(state[0]),
                    'y': float(state[1]),
                    'vx': float(state[2]),
                    'vy': float(state[3]),
                    'ax': float(state[4]),
                    'ay': float(state[5]),
                    'uncertainty': float(uncertainty),
                    'predicted': True,
                    'timestamp': detection.get('timestamp', 0) if 'detection' in locals() else 0
                })
        
        return tracked_objects
    
    def predict_future(self, object_id, steps=10):
        """
        Predict future trajectory using Kalman filter
        
        Args:
            object_id: Object to predict
            steps: Number of future steps
        
        Returns:
            List of predicted positions with uncertainties
        """
        if object_id not in self.trackers:
            return None
        
        kf = self.trackers[object_id]
        predictions = []
        
        # Create a copy for prediction
        future_state = kf.x.copy()
        future_cov = kf.P.copy()
        
        for i in range(1, steps + 1):
            # Propagate state
            future_state = kf.F @ future_state
            future_cov = kf.F @ future_cov @ kf.F.T + kf.Q
            
            # Extract position and uncertainty
            uncertainty = np.sqrt(np.trace(future_cov[:2, :2]))
            
            predictions.append({
                'step': i,
                'x': float(future_state[0]),
                'y': float(future_state[1]),
                'vx': float(future_state[2]),
                'vy': float(future_state[3]),
                'uncertainty': float(uncertainty),
                'confidence': 1.0 / (1.0 + uncertainty)
            })
        
        return predictions
    
    def get_smooth_trajectory(self, object_id, window=10):
        """Get smoothed trajectory for visualization"""
        if object_id not in self.object_states:
            return []
        
        history = self.object_states[object_id]['history'][-window:]
        return [(h['x'], h['y']) for h in history]
    
    def get_tracking_quality(self):
        """Get overall tracking quality metrics"""
        qualities = []
        for obj_id, kf in self.trackers.items():
            uncertainty = np.sqrt(np.trace(kf.P[:2, :2]))
            qualities.append({
                'object_id': obj_id,
                'uncertainty': float(uncertainty),
                'track_length': len(self.object_states.get(obj_id, {}).get('history', []))
            })
        
        return qualities