"""
Threat Intelligence Engine
Multi-factor threat assessment with AI-powered risk analysis
"""

import numpy as np
from collections import deque
import json
from datetime import datetime

class ThreatIntelligence:
    """
    Advanced Threat Assessment System
    
    Factors considered:
    - Proximity to restricted zones
    - Velocity and acceleration
    - Behavioral patterns
    - Historical behavior
    - Predictive trajectory
    - Time of day
    - Group coordination
    """
    
    def __init__(self, config_file='DATA/detection_zones.json'):
        self.threat_zones = self.load_zones(config_file)
        self.object_threats = {}
        self.threat_history = deque(maxlen=1000)
        
        # Threat scoring weights
        self.weights = {
            'proximity': 0.30,
            'velocity': 0.20,
            'behavior': 0.25,
            'history': 0.15,
            'prediction': 0.10
        }
        
        # Threat level thresholds
        self.thresholds = {
            'critical': 85,
            'high': 65,
            'medium': 40,
            'low': 20,
            'negligible': 0
        }
        
    def load_zones(self, config_file):
        """Load restricted zones from config"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default zones
            return {
                'restricted_zones': [
                    {
                        'name': 'Central Zone',
                        'type': 'circle',
                        'x': 50,
                        'y': 50,
                        'radius': 20,
                        'threat_multiplier': 2.0,
                        'priority': 'high'
                    },
                    {
                        'name': 'North Gate',
                        'type': 'rectangle',
                        'x1': 40,
                        'y1': 0,
                        'x2': 60,
                        'y2': 20,
                        'threat_multiplier': 1.5,
                        'priority': 'medium'
                    }
                ]
            }
    
    class ThreatProfile:
        """Threat profile for a single object"""
        
        def __init__(self, object_id):
            self.object_id = object_id
            self.first_seen = datetime.now()
            self.last_seen = datetime.now()
            self.positions = deque(maxlen=100)
            self.threat_scores = deque(maxlen=100)
            self.threat_levels = deque(maxlen=100)
            self.zone_entries = []
            self.risk_factors = []
            
        def update(self, position, timestamp):
            """Update profile with new data"""
            self.last_seen = timestamp
            self.positions.append(position)
            
        def get_duration(self):
            """Get tracking duration in seconds"""
            return (self.last_seen - self.first_seen).total_seconds()
    
    def calculate_threat(self, object_id, position, velocity, behavior_data=None, prediction=None):
        """
        Calculate comprehensive threat score
        
        Args:
            object_id: Object identifier
            position: Current (x, y) position
            velocity: Current (vx, vy) velocity
            behavior_data: Output from behavior analyzer
            prediction: Future trajectory prediction
        
        Returns:
            Complete threat assessment
        """
        # Create profile if new
        if object_id not in self.object_threats:
            self.object_threats[object_id] = self.ThreatProfile(object_id)
        
        profile = self.object_threats[object_id]
        profile.update(position, datetime.now())
        
        # Calculate individual threat factors
        proximity_threat = self._calculate_proximity_threat(position)
        velocity_threat = self._calculate_velocity_threat(velocity)
        behavior_threat = self._calculate_behavior_threat(behavior_data)
        history_threat = self._calculate_history_threat(profile)
        prediction_threat = self._calculate_prediction_threat(prediction, position)
        
        # Weighted combination
        total_score = (
            proximity_threat * self.weights['proximity'] +
            velocity_threat * self.weights['velocity'] +
            behavior_threat * self.weights['behavior'] +
            history_threat * self.weights['history'] +
            prediction_threat * self.weights['prediction']
        )
        
        # Apply time-based modifier
        time_modifier = self._get_time_modifier()
        total_score *= time_modifier
        
        # Apply zone-specific multipliers
        zone_multiplier = self._get_zone_multiplier(position)
        total_score *= zone_multiplier
        
        # Determine threat level
        threat_level = self._get_threat_level(total_score)
        
        # Calculate trend
        threat_trend = self._calculate_trend(profile, total_score)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            proximity_threat, velocity_threat, behavior_threat,
            history_threat, prediction_threat, position
        )
        
        # Store in profile
        profile.threat_scores.append(total_score)
        profile.threat_levels.append(threat_level)
        profile.risk_factors = risk_factors
        
        result = {
            'object_id': object_id,
            'score': float(total_score),
            'level': threat_level,
            'trend': threat_trend,
            'risk_factors': risk_factors,
            'components': {
                'proximity': float(proximity_threat),
                'velocity': float(velocity_threat),
                'behavior': float(behavior_threat),
                'history': float(history_threat),
                'prediction': float(prediction_threat)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in history
        self.threat_history.append(result)
        
        return result
    
    def _calculate_proximity_threat(self, position):
        """Calculate threat based on proximity to restricted zones"""
        x, y = position
        max_threat = 0
        
        for zone in self.threat_zones.get('restricted_zones', []):
            if zone['type'] == 'circle':
                dist = np.sqrt((x - zone['x'])**2 + (y - zone['y'])**2)
                if dist < zone['radius']:
                    # Exponential threat increase as distance decreases
                    threat = 100 * (1 - dist / zone['radius'])
                    threat *= zone.get('threat_multiplier', 1.0)
                    max_threat = max(max_threat, threat)
                    
            elif zone['type'] == 'rectangle':
                if (zone['x1'] <= x <= zone['x2'] and 
                    zone['y1'] <= y <= zone['y2']):
                    threat = 100 * zone.get('threat_multiplier', 1.0)
                    max_threat = max(max_threat, threat)
        
        return min(100, max_threat)
    
    def _calculate_velocity_threat(self, velocity):
        """Calculate threat based on velocity"""
        speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
        
        if speed < 2:
            return 10  # Stationary
        elif speed < 5:
            return 20  # Walking
        elif speed < 10:
            return 40  # Jogging
        elif speed < 20:
            return 60  # Running
        elif speed < 30:
            return 80  # Fast approach
        else:
            return 95  # Very fast (vehicle)
    
    def _calculate_behavior_threat(self, behavior_data):
        """Calculate threat from behavioral analysis"""
        if not behavior_data:
            return 0
        
        # Use behavior score from analyzer
        behavior_score = behavior_data.get('behavior_score', 0)
        threat_multiplier = behavior_data.get('threat_multiplier', 0.5)
        
        return behavior_score * threat_multiplier
    
    def _calculate_history_threat(self, profile):
        """Calculate threat from historical behavior"""
        if len(profile.threat_scores) < 2:
            return 0
        
        # Average of recent scores
        recent = list(profile.threat_scores)[-10:]
        avg_threat = np.mean(recent)
        
        # Check for escalating pattern
        if len(recent) > 5:
            trend = recent[-1] - recent[-5]
            if trend > 20:
                avg_threat *= 1.2
        
        return min(100, avg_threat)
    
    def _calculate_prediction_threat(self, prediction, current_position):
        """Calculate threat based on predicted path"""
        if not prediction or len(prediction) < 3:
            return 0
        
        # Check if predicted path enters restricted zone
        max_future_threat = 0
        for pred in prediction[:3]:  # Look at next 3 steps
            future_pos = (pred['x'], pred['y'])
            future_threat = self._calculate_proximity_threat(future_pos)
            max_future_threat = max(max_future_threat, future_threat)
        
        return max_future_threat
    
    def _get_time_modifier(self):
        """Get threat modifier based on time of day"""
        hour = datetime.now().hour
        
        # Higher threat at night
        if hour < 6 or hour > 22:  # Night (10pm - 6am)
            return 1.5
        elif hour < 8 or hour > 18:  # Dawn/dusk
            return 1.2
        else:
            return 1.0
    
    def _get_zone_multiplier(self, position):
        """Get threat multiplier based on zone priority"""
        x, y = position
        
        for zone in self.threat_zones.get('restricted_zones', []):
            if zone['type'] == 'circle':
                dist = np.sqrt((x - zone['x'])**2 + (y - zone['y'])**2)
                if dist < zone['radius']:
                    if zone.get('priority') == 'high':
                        return 1.5
                    elif zone.get('priority') == 'medium':
                        return 1.2
            elif zone['type'] == 'rectangle':
                if (zone['x1'] <= x <= zone['x2'] and 
                    zone['y1'] <= y <= zone['y2']):
                    if zone.get('priority') == 'high':
                        return 1.5
                    elif zone.get('priority') == 'medium':
                        return 1.2
        
        return 1.0
    
    def _get_threat_level(self, score):
        """Convert numeric score to threat level"""
        if score >= self.thresholds['critical']:
            return 'CRITICAL'
        elif score >= self.thresholds['high']:
            return 'HIGH'
        elif score >= self.thresholds['medium']:
            return 'MEDIUM'
        elif score >= self.thresholds['low']:
            return 'LOW'
        else:
            return 'NEGLIGIBLE'
    
    def _calculate_trend(self, profile, current_score):
        """Calculate threat score trend"""
        if len(profile.threat_scores) < 5:
            return 'stable'
        
        recent = list(profile.threat_scores)[-5:]
        if recent[-1] > recent[0] * 1.2:
            return 'increasing'
        elif recent[-1] < recent[0] * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _identify_risk_factors(self, *factors, position):
        """Identify specific risk factors"""
        risk_factors = []
        names = ['proximity', 'velocity', 'behavior', 'history', 'prediction']
        
        for name, score in zip(names, factors):
            if score > 70:
                risk_factors.append({
                    'factor': name,
                    'severity': 'HIGH',
                    'score': score,
                    'description': self._get_factor_description(name, score)
                })
            elif score > 40:
                risk_factors.append({
                    'factor': name,
                    'severity': 'MEDIUM',
                    'score': score,
                    'description': self._get_factor_description(name, score)
                })
        
        # Add position-specific factors
        x, y = position
        if x < 10 or x > 90 or y < 10 or y > 90:
            risk_factors.append({
                'factor': 'boundary',
                'severity': 'MEDIUM',
                'score': 50,
                'description': 'Object near area boundary'
            })
        
        return risk_factors
    
    def _get_factor_description(self, factor, score):
        """Get description for risk factor"""
        descriptions = {
            'proximity': 'Close to restricted zone',
            'velocity': 'High speed movement',
            'behavior': 'Suspicious behavior pattern',
            'history': 'Consistent threatening behavior',
            'prediction': 'Predicted to enter restricted zone',
            'boundary': 'Operating near boundary'
        }
        return descriptions.get(factor, 'Unknown risk factor')
    
    def get_threat_summary(self):
        """Get summary of current threats"""
        summary = {
            'total_objects': len(self.object_threats),
            'threat_counts': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'NEGLIGIBLE': 0
            },
            'average_threat': 0,
            'highest_threat': None
        }
        
        total_score = 0
        max_score = 0
        
        for obj_id, profile in self.object_threats.items():
            if profile.threat_scores:
                current_score = profile.threat_scores[-1]
                level = self._get_threat_level(current_score)
                summary['threat_counts'][level] += 1
                total_score += current_score
                
                if current_score > max_score:
                    max_score = current_score
                    summary['highest_threat'] = obj_id
        
        if summary['total_objects'] > 0:
            summary['average_threat'] = total_score / summary['total_objects']
        
        return summary