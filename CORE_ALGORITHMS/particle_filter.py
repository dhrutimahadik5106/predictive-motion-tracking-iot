"""
Particle Filter for Multi-Hypothesis Tracking
Handles occlusions and non-linear movements
"""

import numpy as np
from collections import deque
import random

class ParticleFilter:
    """
    Particle Filter for robust object tracking
    
    Features:
    - Multiple hypotheses
    - Occlusion handling
    - Non-linear movement support
    - Uncertainty estimation
    """
    
    def __init__(self, num_particles=500):
        self.num_particles = num_particles
        self.trackers = {}  # object_id -> particle set
        self.resample_threshold = 0.5
        
    class ParticleSet:
        """Particle set for a single object"""
        
        def __init__(self, parent, initial_position=None):
            self.parent = parent
            self.particles = []
            self.weights = []
            self.age = 0
            self.occlusion_count = 0
            self.trajectory = deque(maxlen=50)
            
            if initial_position:
                self.initialize_around_position(initial_position)
            else:
                self.initialize_random()
        
        def initialize_around_position(self, position, spread=5):
            """Initialize particles around a known position"""
            x, y = position
            for _ in range(self.parent.num_particles):
                particle = np.array([
                    x + np.random.normal(0, spread),
                    y + np.random.normal(0, spread),
                    np.random.normal(0, 2),  # vx
                    np.random.normal(0, 2),  # vy
                    1.0  # weight factor
                ])
                self.particles.append(particle)
                self.weights.append(1.0 / self.parent.num_particles)
        
        def initialize_random(self):
            """Random initialization"""
            for _ in range(self.parent.num_particles):
                particle = np.array([
                    np.random.uniform(0, 100),
                    np.random.uniform(0, 100),
                    np.random.normal(0, 2),
                    np.random.normal(0, 2),
                    1.0
                ])
                self.particles.append(particle)
                self.weights.append(1.0 / self.parent.num_particles)
        
        def predict(self, dt=0.1):
            """Predict step: move particles according to motion model"""
            for i, particle in enumerate(self.particles):
                # Simple motion model
                particle[0] += particle[2] * dt  # x += vx * dt
                particle[1] += particle[3] * dt  # y += vy * dt
                
                # Add random noise (process noise)
                particle[0] += np.random.normal(0, 1)
                particle[1] += np.random.normal(0, 1)
                particle[2] += np.random.normal(0, 0.5)
                particle[3] += np.random.normal(0, 0.5)
                
                # Boundaries
                particle[0] = np.clip(particle[0], 0, 100)
                particle[1] = np.clip(particle[1], 0, 100)
                
                self.particles[i] = particle
        
        def update_weights(self, measurement, measurement_noise=5):
            """Update particle weights based on measurement"""
            if measurement is None:
                # No measurement - all weights equal (just predict)
                return
            
            x_meas, y_meas = measurement
            
            for i, particle in enumerate(self.particles):
                # Distance from particle to measurement
                dist = np.sqrt((particle[0] - x_meas)**2 + (particle[1] - y_meas)**2)
                
                # Gaussian likelihood
                likelihood = np.exp(-(dist**2) / (2 * measurement_noise**2))
                
                # Update weight
                self.weights[i] *= likelihood
            
            # Normalize weights
            weight_sum = sum(self.weights)
            if weight_sum > 0:
                self.weights = [w / weight_sum for w in self.weights]
            else:
                # If all weights zero, reset to uniform
                self.weights = [1.0 / len(self.particles)] * len(self.particles)
        
        def resample(self):
            """Resample particles based on weights"""
            # Calculate effective sample size
            ess = 1.0 / sum(w**2 for w in self.weights)
            
            if ess / len(self.particles) < self.parent.resample_threshold:
                # Systematic resampling
                new_particles = []
                positions = np.cumsum(self.weights)
                step = 1.0 / len(self.particles)
                position = np.random.uniform(0, step)
                
                for _ in range(len(self.particles)):
                    position += step
                    idx = np.searchsorted(positions, position)
                    
                    # Add small random noise to maintain diversity
                    new_particle = self.particles[idx].copy()
                    new_particle[0] += np.random.normal(0, 0.5)
                    new_particle[1] += np.random.normal(0, 0.5)
                    
                    new_particles.append(new_particle)
                
                self.particles = new_particles
                self.weights = [1.0 / len(self.particles)] * len(self.particles)
                return True
            
            return False
        
        def estimate_state(self):
            """Estimate current state from particle distribution"""
            if not self.particles:
                return None
            
            # Weighted mean
            mean = np.zeros(5)
            for i, particle in enumerate(self.particles):
                mean += self.weights[i] * particle
            
            # Covariance for uncertainty
            cov = np.zeros((5, 5))
            for i, particle in enumerate(self.particles):
                diff = particle - mean
                cov += self.weights[i] * np.outer(diff, diff)
            
            # Uncertainty (trace of position covariance)
            uncertainty = np.sqrt(np.trace(cov[:2, :2]))
            
            # Store trajectory
            self.trajectory.append((mean[0], mean[1]))
            self.age += 1
            
            return {
                'x': mean[0],
                'y': mean[1],
                'vx': mean[2],
                'vy': mean[3],
                'confidence': mean[4],
                'uncertainty': uncertainty,
                'covariance': cov.tolist()
            }
        
        def get_particle_distribution(self):
            """Get all particles for visualization"""
            return [(p[0], p[1], w) for p, w in zip(self.particles, self.weights)]
    
    def update(self, detections):
        """
        Update particle filters with new detections
        """
        tracked_objects = []
        
        # Update existing trackers
        for obj_id, particle_set in list(self.trackers.items()):
            # Find matching detection
            matching_detection = next(
                (d for d in detections if d.get('id') == obj_id),
                None
            )
            
            if matching_detection:
                measurement = (matching_detection['x'], matching_detection['y'])
                particle_set.occlusion_count = 0
            else:
                measurement = None
                particle_set.occlusion_count += 1
            
            # Predict
            particle_set.predict()
            
            # Update weights
            particle_set.update_weights(measurement)
            
            # Resample
            particle_set.resample()
            
            # Estimate state
            state = particle_set.estimate_state()
            
            if state:
                # Check if object lost
                if particle_set.occlusion_count > 20:
                    del self.trackers[obj_id]
                else:
                    tracked_objects.append({
                        'id': obj_id,
                        'x': state['x'],
                        'y': state['y'],
                        'vx': state['vx'],
                        'vy': state['vy'],
                        'confidence': state['confidence'],
                        'uncertainty': state['uncertainty'],
                        'occluded': particle_set.occlusion_count > 0,
                        'particle_count': len(particle_set.particles)
                    })
        
        # Create new trackers for unmatched detections
        existing_ids = set(self.trackers.keys())
        for detection in detections:
            obj_id = detection.get('id')
            if obj_id not in existing_ids:
                particle_set = self.ParticleSet(
                    self,
                    initial_position=(detection['x'], detection['y'])
                )
                self.trackers[obj_id] = particle_set
        
        return tracked_objects
    
    def predict_future(self, object_id, steps=10):
        """
        Predict future trajectory using particle propagation
        """
        if object_id not in self.trackers:
            return None
        
        particle_set = self.trackers[object_id]
        predictions = []
        
        # Propagate particles forward
        for step in range(1, steps + 1):
            step_particles = []
            
            for particle in particle_set.particles:
                # Propagate
                future_x = particle[0] + particle[2] * step * 0.1
                future_y = particle[1] + particle[3] * step * 0.1
                
                # Add uncertainty that grows with time
                future_x += np.random.normal(0, np.sqrt(step))
                future_y += np.random.normal(0, np.sqrt(step))
                
                step_particles.append((future_x, future_y))
            
            # Calculate distribution
            x_vals = [p[0] for p in step_particles]
            y_vals = [p[1] for p in step_particles]
            
            predictions.append({
                'step': step,
                'x': np.mean(x_vals),
                'y': np.mean(y_vals),
                'std_x': np.std(x_vals),
                'std_y': np.std(y_vals),
                'confidence': 1.0 / (1.0 + np.std(x_vals) + np.std(y_vals))
            })
        
        return predictions
    
    def get_particles_for_visualization(self, object_id):
        """Get particles for 3D visualization"""
        if object_id not in self.trackers:
            return []
        
        particle_set = self.trackers[object_id]
        return [(p[0], p[1], w) for p, w in zip(particle_set.particles, particle_set.weights)]