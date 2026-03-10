"""
AI-POWERED BEHAVIOR ANALYZER
Uses Machine Learning to detect and classify object behaviors in real-time
"""

import numpy as np
from collections import deque
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AIBehaviorAnalyzer:
    """
    Advanced Behavior Analysis with Machine Learning
    
    Detects:
    - Loitering / Stalking
    - Rapid Approach / Charging
    - Zigzag / Evasive Maneuvers
    - Patrolling / Systematic Search
    - Following / Shadowing
    - Waiting / Ambush Preparation
    - Normal / Innocuous Movement
    """
    
    def __init__(self, model_path=None):
        self.object_histories = {}  # object_id -> history
        self.behavior_predictions = {}
        self.behavior_scores = {}
        
        # Behavior categories with descriptions
        self.behavior_categories = {
            'loitering': {
                'description': 'Prolonged stay in same area',
                'threat_multiplier': 0.7,
                'color': '#ffaa00',
                'indicators': ['low_movement', 'long_duration', 'area_focus']
            },
            'rapid_approach': {
                'description': 'High-speed direct approach',
                'threat_multiplier': 1.5,
                'color': '#ff4444',
                'indicators': ['high_speed', 'direct_path', 'closing_distance']
            },
            'evasive_maneuvers': {
                'description': 'Erratic movement to avoid detection',
                'threat_multiplier': 1.3,
                'color': '#ff6600',
                'indicators': ['high_angular_velocity', 'sudden_direction_changes']
            },
            'patrolling': {
                'description': 'Systematic area coverage',
                'threat_multiplier': 0.9,
                'color': '#ffaa00',
                'indicators': ['regular_pattern', 'area_coverage', 'periodic_return']
            },
            'following': {
                'description': 'Tracking another object',
                'threat_multiplier': 1.1,
                'color': '#ff8800',
                'indicators': ['maintaining_distance', 'matching_movements']
            },
            'waiting': {
                'description': 'Stationary in strategic location',
                'threat_multiplier': 1.2,
                'color': '#ff5500',
                'indicators': ['stationary', 'strategic_position', 'duration']
            },
            'normal': {
                'description': 'Normal movement pattern',
                'threat_multiplier': 0.3,
                'color': '#00ff88',
                'indicators': ['predictable', 'consistent_speed', 'direct_path']
            },
            'suspicious': {
                'description': 'Unusual but undefined behavior',
                'threat_multiplier': 0.8,
                'color': '#ffaa00',
                'indicators': ['unpredictable', 'inconsistent', 'anomalous']
            }
        }
        
        # ML Model for behavior classification
        self.model = self._create_model()
        self.scaler = StandardScaler()
        self.model_trained = False
        
        # Feature extraction parameters
        self.history_length = 50
        self.analysis_window = 20
        
        # Load pre-trained model if available
        if model_path:
            self.load_model(model_path)
        else:
            # Train with synthetic data for demo
            self._train_with_synthetic_data()
    
    def _create_model(self):
        """Create Random Forest classifier for behavior detection"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
    
    def _train_with_synthetic_data(self):
        """Train model with synthetic data for demonstration"""
        print("🤖 Training AI Behavior Analyzer with synthetic data...")
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        X_train = []
        y_train = []
        
        for _ in range(n_samples):
            # Generate random features
            features = self._generate_synthetic_features()
            X_train.append(features)
            
            # Assign behavior based on features
            behavior = self._assign_behavior_from_features(features)
            y_train.append(behavior)
        
        X_train = np.array(X_train)
        
        # Fit scaler
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.model_trained = True
        print("✅ AI Behavior Analyzer trained successfully!")
    
    def _generate_synthetic_features(self):
        """Generate synthetic feature vector for training"""
        features = [
            np.random.uniform(0, 50),  # avg_speed
            np.random.uniform(0, 30),  # max_speed
            np.random.uniform(0, 20),  # speed_variance
            np.random.uniform(0, 180),  # avg_direction_change
            np.random.uniform(0, 360),  # max_direction_change
            np.random.uniform(0, 100),  # movement_consistency
            np.random.uniform(0, 100),  # area_coverage
            np.random.uniform(0, 60),  # stationary_duration
            np.random.uniform(0, 50),  # distance_to_center
            np.random.uniform(0, 2),  # acceleration
            np.random.uniform(0, 1),  # path_curvature
            np.random.uniform(0, 1),  # periodicity
        ]
        return features
    
    def _assign_behavior_from_features(self, features):
        """Assign behavior based on feature values"""
        speed, max_speed, speed_var, dir_change, max_dir, consistency, coverage, stationary, dist, acc, curvature, period = features
        
        if stationary > 30 and dist < 30:
            return 'waiting'
        elif speed > 30 and consistency > 80:
            return 'rapid_approach'
        elif dir_change > 90 and speed_var > 10:
            return 'evasive_maneuvers'
        elif period > 0.7 and coverage > 60:
            return 'patrolling'
        elif speed < 5 and stationary < 10 and dist > 30:
            return 'normal'
        elif speed < 15 and dist < 20 and stationary > 10:
            return 'loitering'
        else:
            return 'suspicious'
    
    def extract_features(self, object_id, positions, timestamps, velocities):
        """
        Extract behavioral features from tracking data
        
        Args:
            object_id: ID of the object
            positions: List of (x, y) positions
            timestamps: List of timestamps
            velocities: List of (vx, vy) velocities
        
        Returns:
            Feature vector for ML model
        """
        if len(positions) < 5:
            return None
        
        # Convert to numpy arrays
        pos_array = np.array(positions)
        vel_array = np.array(velocities)
        
        # Speed features
        speeds = np.sqrt(vel_array[:, 0]**2 + vel_array[:, 1]**2)
        avg_speed = np.mean(speeds)
        max_speed = np.max(speeds)
        speed_variance = np.var(speeds)
        
        # Direction features
        directions = np.arctan2(vel_array[:, 1], vel_array[:, 0])
        direction_changes = np.abs(np.diff(directions)) * 180 / np.pi
        avg_direction_change = np.mean(direction_changes) if len(direction_changes) > 0 else 0
        max_direction_change = np.max(direction_changes) if len(direction_changes) > 0 else 0
        
        # Movement consistency (how straight the path is)
        if len(pos_array) > 1:
            total_path = np.sum(np.sqrt(np.sum(np.diff(pos_array, axis=0)**2, axis=1)))
            straight_line = np.linalg.norm(pos_array[-1] - pos_array[0])
            movement_consistency = straight_line / total_path if total_path > 0 else 0
        else:
            movement_consistency = 0
        
        # Area coverage (bounding box area)
        x_range = np.max(pos_array[:, 0]) - np.min(pos_array[:, 0])
        y_range = np.max(pos_array[:, 1]) - np.min(pos_array[:, 1])
        area_coverage = x_range * y_range / 10000  # Normalized
        
        # Stationary duration
        stationary_threshold = 2  # cm/s
        stationary_frames = np.sum(speeds < stationary_threshold)
        stationary_duration = stationary_frames / len(speeds) * 100  # Percentage
        
        # Distance to restricted zone (center at 50,50)
        if len(pos_array) > 0:
            distances_to_center = np.sqrt((pos_array[:, 0] - 50)**2 + (pos_array[:, 1] - 50)**2)
            avg_distance = np.mean(distances_to_center)
            min_distance = np.min(distances_to_center)
        else:
            avg_distance = 50
            min_distance = 50
        
        # Acceleration features
        if len(vel_array) > 2:
            accel = np.diff(vel_array, axis=0) / 0.1  # Assuming 10Hz
            avg_accel = np.mean(np.sqrt(accel[:, 0]**2 + accel[:, 1]**2))
        else:
            avg_accel = 0
        
        # Path curvature
        if len(pos_array) > 2:
            # Simplified curvature estimation
            vectors = pos_array[1:] - pos_array[:-1]
            if len(vectors) > 1:
                dot_products = np.sum(vectors[:-1] * vectors[1:], axis=1)
                norms = np.linalg.norm(vectors[:-1], axis=1) * np.linalg.norm(vectors[1:], axis=1)
                cos_angles = dot_products / (norms + 1e-6)
                avg_curvature = np.mean(np.arccos(np.clip(cos_angles, -1, 1))) / np.pi
            else:
                avg_curvature = 0
        else:
            avg_curvature = 0
        
        # Periodicity detection (simplified)
        if len(positions) > 10:
            # Check if object returns to previous positions
            recent_pos = pos_array[-10:]
            unique_positions = len(np.unique(recent_pos, axis=0))
            periodicity = 1 - (unique_positions / 10)
        else:
            periodicity = 0
        
        features = [
            avg_speed,
            max_speed,
            speed_variance,
            avg_direction_change,
            max_direction_change,
            movement_consistency * 100,
            area_coverage * 100,
            stationary_duration,
            avg_distance,
            avg_accel,
            avg_curvature,
            periodicity
        ]
        
        return np.array(features)
    
    def analyze_behavior(self, object_id, position, velocity, timestamp, all_objects=None):
        """
        Analyze behavior of a single object using AI
        
        Args:
            object_id: Object identifier
            position: Current (x, y) position
            velocity: Current (vx, vy) velocity
            timestamp: Current timestamp
            all_objects: List of all tracked objects (for interaction analysis)
        
        Returns:
            Behavior analysis result with confidence scores
        """
        # Initialize history for new object
        if object_id not in self.object_histories:
            self.object_histories[object_id] = {
                'positions': deque(maxlen=self.history_length),
                'timestamps': deque(maxlen=self.history_length),
                'velocities': deque(maxlen=self.history_length),
                'first_seen': timestamp,
                'last_behavior': None
            }
        
        # Update history
        history = self.object_histories[object_id]
        history['positions'].append(position)
        history['timestamps'].append(timestamp)
        history['velocities'].append(velocity)
        
        # Need enough history for analysis
        if len(history['positions']) < 10:
            return {
                'object_id': object_id,
                'primary_behavior': 'analyzing',
                'confidence': 0.3,
                'all_behaviors': {},
                'description': 'Collecting data for behavior analysis...',
                'threat_multiplier': 0.5
            }
        
        # Extract features
        features = self.extract_features(
            object_id,
            list(history['positions']),
            list(history['timestamps']),
            list(history['velocities'])
        )
        
        if features is None:
            return None
        
        # Scale features
        if self.model_trained:
            features_scaled = self.scaler.transform([features])
            
            # Get probability predictions from ML model
            probabilities = self.model.predict_proba(features_scaled)[0]
            behavior_classes = self.model.classes_
            
            # Create behavior dictionary with probabilities
            behaviors = {}
            for i, behavior in enumerate(behavior_classes):
                behaviors[behavior] = float(probabilities[i])
            
            # Get primary behavior (highest probability)
            primary_idx = np.argmax(probabilities)
            primary_behavior = behavior_classes[primary_idx]
            confidence = float(probabilities[primary_idx])
        else:
            # Fallback to rule-based if model not trained
            behaviors, primary_behavior, confidence = self._rule_based_analysis(features)
        
        # Check for interactions with other objects
        interaction_analysis = self._analyze_interactions(object_id, position, all_objects)
        
        # Adjust behavior based on interactions
        if interaction_analysis['following']:
            behaviors['following'] = behaviors.get('following', 0) + 0.3
            if behaviors['following'] > confidence:
                primary_behavior = 'following'
                confidence = behaviors['following']
        
        # Store current behavior
        self.behavior_predictions[object_id] = {
            'primary': primary_behavior,
            'confidence': confidence,
            'timestamp': timestamp
        }
        
        # Calculate behavior score (0-100)
        behavior_score = self._calculate_behavior_score(primary_behavior, confidence, features)
        
        # Get behavior category info
        behavior_info = self.behavior_categories.get(primary_behavior, self.behavior_categories['suspicious'])
        
        # Generate natural language description
        description = self._generate_description(
            primary_behavior, 
            confidence, 
            features,
            interaction_analysis
        )
        
        result = {
            'object_id': object_id,
            'primary_behavior': primary_behavior,
            'confidence': confidence,
            'all_behaviors': {k: float(v) for k, v in behaviors.items()},
            'description': description,
            'threat_multiplier': behavior_info['threat_multiplier'],
            'color': behavior_info['color'],
            'behavior_score': behavior_score,
            'features': {
                'speed': float(features[0]),
                'direction_change': float(features[3]),
                'consistency': float(features[5]),
                'stationary': float(features[7]),
                'curvature': float(features[10])
            },
            'interactions': interaction_analysis,
            'duration': (timestamp - history['first_seen']).total_seconds() if hasattr(timestamp, 'total_seconds') else 0
        }
        
        # Store for later use
        history['last_behavior'] = result
        
        return result
    
    def _rule_based_analysis(self, features):
        """Fallback rule-based behavior analysis"""
        speed, max_speed, speed_var, dir_change, max_dir, consistency, coverage, stationary, dist, acc, curvature, period = features
        
        behaviors = {}
        
        # Rule-based scoring
        if stationary > 30 and dist < 30:
            behaviors['waiting'] = stationary / 100
        if speed > 30 and consistency > 80:
            behaviors['rapid_approach'] = (speed / 50) * (consistency / 100)
        if dir_change > 90 and speed_var > 10:
            behaviors['evasive_maneuvers'] = (dir_change / 180) * (speed_var / 20)
        if period > 0.7 and coverage > 60:
            behaviors['patrolling'] = period * (coverage / 100)
        if speed < 5 and stationary < 10 and dist > 30:
            behaviors['normal'] = 1 - (speed / 10)
        if speed < 15 and dist < 20 and stationary > 10:
            behaviors['loitering'] = (stationary / 50) * (1 - dist / 50)
        
        # Ensure at least one behavior
        if not behaviors:
            behaviors['suspicious'] = 0.5
        
        # Normalize
        total = sum(behaviors.values())
        behaviors = {k: v/total for k, v in behaviors.items()}
        
        # Get primary
        primary = max(behaviors, key=behaviors.get)
        confidence = behaviors[primary]
        
        return behaviors, primary, confidence
    
    def _analyze_interactions(self, object_id, position, all_objects):
        """Analyze interactions with other objects"""
        if not all_objects:
            return {'following': False, 'avoiding': False, 'meeting': False}
        
        result = {
            'following': False,
            'following_id': None,
            'avoiding': False,
            'meeting': False,
            'nearby_objects': []
        }
        
        current_pos = np.array(position)
        
        for other in all_objects:
            if other['id'] == object_id:
                continue
            
            other_pos = np.array([other['x'], other['y']])
            distance = np.linalg.norm(current_pos - other_pos)
            
            if distance < 20:
                result['nearby_objects'].append({
                    'id': other['id'],
                    'distance': float(distance)
                })
                
                # Check if following (similar path and maintaining distance)
                if distance < 15 and distance > 5:
                    result['following'] = True
                    result['following_id'] = other['id']
                
                # Check if meeting (converging paths)
                if distance < 10 and distance > 2:
                    result['meeting'] = True
        
        return result
    
    def _calculate_behavior_score(self, behavior, confidence, features):
        """Calculate a score (0-100) for the behavior"""
        base_scores = {
            'normal': 20,
            'loitering': 50,
            'patrolling': 40,
            'suspicious': 60,
            'following': 65,
            'waiting': 55,
            'rapid_approach': 85,
            'evasive_maneuvers': 90
        }
        
        base = base_scores.get(behavior, 50)
        
        # Adjust based on features
        speed, _, _, dir_change, _, _, _, stationary, dist, acc, curvature, _ = features
        
        # Faster movement increases score
        if speed > 20:
            base += 15
        elif speed > 10:
            base += 5
        
        # Erratic movement increases score
        if dir_change > 90:
            base += 10
        
        # Close to center increases score
        if dist < 20:
            base += 20
        elif dist < 40:
            base += 10
        
        # Apply confidence
        score = base * confidence
        
        return min(100, max(0, score))
    
    def _generate_description(self, behavior, confidence, features, interactions):
        """Generate natural language description of behavior"""
        speed, max_speed, speed_var, dir_change, max_dir, consistency, coverage, stationary, dist, acc, curvature, period = features
        
        descriptions = {
            'loitering': f"Object lingering in area for {stationary:.0f}% of time. {confidence*100:.0f}% confidence.",
            'rapid_approach': f"Fast approach at {speed:.1f} cm/s. Direct path with {consistency:.0f}% consistency.",
            'evasive_maneuvers': f"Erratic movement with {dir_change:.0f}° direction changes. Possible evasive action.",
            'patrolling': f"Systematic coverage of {coverage:.0f}% of area. Periodic pattern detected.",
            'following': f"Following object {interactions.get('following_id')} at close distance.",
            'waiting': f"Stationary for {stationary:.0f}% of time at strategic position.",
            'normal': f"Normal movement at {speed:.1f} cm/s. Predictable path.",
            'suspicious': f"Unusual behavior pattern. Further observation recommended."
        }
        
        return descriptions.get(behavior, "Behavior under analysis")
    
    def get_all_behaviors(self):
        """Get current behaviors for all objects"""
        return self.behavior_predictions
    
    def get_behavior_summary(self):
        """Get summary of all behaviors"""
        summary = {
            'total_objects': len(self.object_histories),
            'behavior_counts': {},
            'avg_confidence': 0,
            'highest_threat': None
        }
        
        total_conf = 0
        max_threat = 0
        
        for obj_id, behavior_data in self.behavior_predictions.items():
            behavior = behavior_data['primary']
            summary['behavior_counts'][behavior] = summary['behavior_counts'].get(behavior, 0) + 1
            total_conf += behavior_data['confidence']
            
            threat_mult = self.behavior_categories.get(behavior, {}).get('threat_multiplier', 0.5)
            if threat_mult > max_threat:
                max_threat = threat_mult
                summary['highest_threat'] = obj_id
        
        if summary['total_objects'] > 0:
            summary['avg_confidence'] = total_conf / summary['total_objects']
        
        return summary