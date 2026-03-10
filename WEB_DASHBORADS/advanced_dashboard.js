/**
 * ADVANCED DASHBOARD CONTROLLER
 * Patent Feature: Real-time multi-object tracking visualization with AI insights
 */

class AdvancedDashboard {
    constructor() {
        this.config = {
            refreshRate: 200, // ms
            maxHistoryPoints: 100,
            alertThresholds: {
                low: 30,
                medium: 60,
                high: 80,
                critical: 95
            }
        };
        
        this.data = {
            objects: [],
            threats: [],
            history: [],
            systemHealth: {},
            alerts: []
        };
        
        this.charts = {};
        this.init();
    }
    
    init() {
        this.loadConfig();
        this.initCharts();
        this.initEventListeners();
        this.startDataStream();
        this.initWebSocket();
    }
    
    loadConfig() {
        // Load configuration from localStorage or server
        const savedConfig = localStorage.getItem('dashboardConfig');
        if (savedConfig) {
            this.config = {...this.config, ...JSON.parse(savedConfig)};
        }
    }
    
    initCharts() {
        // Threat Timeline Chart
        const threatCtx = document.getElementById('threatTimelineChart').getContext('2d');
        this.charts.threatTimeline = new Chart(threatCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Object 1 Threat',
                    data: [],
                    borderColor: '#ff4444',
                    backgroundColor: 'transparent',
                    tension: 0.4
                }, {
                    label: 'Object 2 Threat',
                    data: [],
                    borderColor: '#ffaa00',
                    backgroundColor: 'transparent',
                    tension: 0.4
                }, {
                    label: 'Object 3 Threat',
                    data: [],
                    borderColor: '#00ff88',
                    backgroundColor: 'transparent',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 0 },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: '#2a3248' },
                        title: { display: true, text: 'Threat Level (%)', color: '#888' }
                    },
                    x: {
                        grid: { display: false },
                        title: { display: true, text: 'Time', color: '#888' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
        
        // Detection Rate Chart
        const detectionCtx = document.getElementById('detectionRateChart').getContext('2d');
        this.charts.detectionRate = new Chart(detectionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Sensor 1', 'Sensor 2', 'Sensor 3'],
                datasets: [{
                    data: [33, 33, 34],
                    backgroundColor: ['#ff4444', '#00ff88', '#4444ff'],
                    borderColor: '#1a1f2f',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
        
        // Velocity Distribution Chart
        const velocityCtx = document.getElementById('velocityChart').getContext('2d');
        this.charts.velocity = new Chart(velocityCtx, {
            type: 'bar',
            data: {
                labels: ['Object 1', 'Object 2', 'Object 3'],
                datasets: [{
                    label: 'Speed (cm/s)',
                    data: [0, 0, 0],
                    backgroundColor: '#00ff88',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#2a3248' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
    
    initEventListeners() {
        // Refresh rate slider
        document.getElementById('refreshRate')?.addEventListener('input', (e) => {
            this.config.refreshRate = e.target.value;
            document.getElementById('refreshValue').textContent = `${e.target.value}ms`;
            this.restartDataStream();
        });
        
        // Alert threshold sliders
        ['low', 'medium', 'high', 'critical'].forEach(level => {
            document.getElementById(`threshold_${level}`)?.addEventListener('input', (e) => {
                this.config.alertThresholds[level] = parseInt(e.target.value);
                document.getElementById(`threshold_${level}_value`).textContent = e.target.value;
            });
        });
        
        // Export data button
        document.getElementById('exportData')?.addEventListener('click', () => {
            this.exportTrackingData();
        });
        
        // Clear history button
        document.getElementById('clearHistory')?.addEventListener('click', () => {
            this.clearHistory();
        });
    }
    
    initWebSocket() {
        // In production, connect to real WebSocket server
        // For simulation, we'll use setInterval
        console.log('WebSocket initialized (simulation mode)');
    }
    
    startDataStream() {
        this.dataInterval = setInterval(() => {
            this.fetchData();
        }, this.config.refreshRate);
    }
    
    restartDataStream() {
        if (this.dataInterval) {
            clearInterval(this.dataInterval);
        }
        this.startDataStream();
    }
    
    fetchData() {
        // Simulate fetching data from server
        // In production, this would be an API call
        const newData = this.generateSimulatedData();
        this.updateDashboard(newData);
    }
    
    generateSimulatedData() {
        const timestamp = Date.now();
        const objects = [];
        
        // Generate 1-3 objects
        const numObjects = Math.floor(Math.random() * 3) + 1;
        
        for (let i = 0; i < numObjects; i++) {
            // Generate object with realistic movement
            const time = timestamp / 1000;
            const obj = {
                id: i + 1,
                x: 50 + 30 * Math.sin(time * 0.1 + i * 2),
                y: 50 + 20 * Math.cos(time * 0.13 + i * 2),
                vx: 3 * Math.cos(time * 0.1 + i * 2),
                vy: -2.6 * Math.sin(time * 0.13 + i * 2),
                confidence: 0.7 + Math.random() * 0.3,
                threatScore: 30 + Math.random() * 60,
                type: i === 0 ? 'intruder' : 'patrol',
                sensorReadings: {
                    s1: 20 + Math.random() * 30,
                    s2: 25 + Math.random() * 30,
                    s3: 22 + Math.random() * 30
                }
            };
            
            // Calculate threat level based on position
            const distToCenter = Math.sqrt((obj.x - 50)**2 + (obj.y - 50)**2);
            obj.threatScore = Math.min(100, Math.max(0, 80 - distToCenter + Math.random() * 20));
            obj.threatLevel = this.getThreatLevel(obj.threatScore);
            
            objects.push(obj);
        }
        
        // Calculate system health
        const systemHealth = {
            cpu: 20 + Math.random() * 30,
            memory: 30 + Math.random() * 20,
            uptime: Math.floor(Date.now() / 1000),
            trackingAccuracy: 85 + Math.random() * 10,
            fps: Math.floor(1000 / this.config.refreshRate)
        };
        
        // Generate alerts based on threat levels
        const alerts = [];
        objects.forEach(obj => {
            if (obj.threatScore > 70) {
                alerts.push({
                    id: Date.now() + obj.id,
                    type: 'HIGH_THREAT',
                    message: `Object ${obj.id} entering restricted zone`,
                    severity: 'critical',
                    timestamp: new Date().toLocaleTimeString()
                });
            } else if (obj.threatScore > 40 && Math.random() > 0.7) {
                alerts.push({
                    id: Date.now() + obj.id,
                    type: 'SUSPICIOUS_BEHAVIOR',
                    message: `Object ${obj.id} showing unusual pattern`,
                    severity: 'warning',
                    timestamp: new Date().toLocaleTimeString()
                });
            }
        });
        
        return {
            timestamp,
            objects,
            systemHealth,
            alerts: alerts.slice(0, 5) // Limit to 5 alerts
        };
    }
    
    updateDashboard(data) {
        this.data = {...this.data, ...data};
        
        // Update object list
        this.updateObjectList(data.objects);
        
        // Update threat meters
        this.updateThreatMeters(data.objects);
        
        // Update system health
        this.updateSystemHealth(data.systemHealth);
        
        // Update alerts
        this.updateAlerts(data.alerts);
        
        // Update charts
        this.updateCharts(data);
        
        // Update heatmap data (for heatmap generator)
        if (window.heatmapGenerator) {
            window.heatmapGenerator.updateData(data.objects);
        }
        
        // Update 3D visualization (for 3D visualizer)
        if (window.visualizer3D) {
            window.visualizer3D.updateObjects(data.objects);
        }
    }
    
    updateObjectList(objects) {
        const container = document.getElementById('objectList');
        if (!container) return;
        
        container.innerHTML = objects.map(obj => `
            <div class="object-card ${obj.threatLevel.toLowerCase()}" 
                 onclick="dashboard.showObjectDetails(${obj.id})">
                <div class="object-header">
                    <span class="object-id">Object #${obj.id}</span>
                    <span class="object-type ${obj.type}">${obj.type}</span>
                </div>
                <div class="object-details">
                    <div class="detail-row">
                        <span class="detail-label">Position:</span>
                        <span class="detail-value">(${obj.x.toFixed(1)}, ${obj.y.toFixed(1)})</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Speed:</span>
                        <span class="detail-value">${Math.sqrt(obj.vx**2 + obj.vy**2).toFixed(1)} cm/s</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Confidence:</span>
                        <span class="detail-value">${(obj.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div class="threat-indicator">
                        <div class="threat-label">Threat Level:</div>
                        <div class="threat-bar">
                            <div class="threat-fill ${obj.threatLevel.toLowerCase()}" 
                                 style="width: ${obj.threatScore}%"></div>
                        </div>
                        <div class="threat-score">${obj.threatScore.toFixed(0)}%</div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    updateThreatMeters(objects) {
        // Update global threat meter
        const globalThreat = objects.reduce((sum, obj) => sum + obj.threatScore, 0) / objects.length;
        document.getElementById('globalThreatFill').style.width = `${globalThreat}%`;
        document.getElementById('globalThreatValue').textContent = `${globalThreat.toFixed(0)}%`;
        
        // Update individual threat meters
        objects.forEach((obj, index) => {
            const meter = document.getElementById(`threatMeter${index + 1}`);
            if (meter) {
                meter.style.width = `${obj.threatScore}%`;
                meter.className = `threat-fill ${obj.threatLevel.toLowerCase()}`;
            }
        });
    }
    
    updateSystemHealth(health) {
        document.getElementById('cpuUsage').textContent = `${health.cpu.toFixed(0)}%`;
        document.getElementById('memoryUsage').textContent = `${health.memory.toFixed(0)}%`;
        document.getElementById('uptime').textContent = this.formatUptime(health.uptime);
        document.getElementById('trackingAccuracy').textContent = `${health.trackingAccuracy.toFixed(0)}%`;
        document.getElementById('fps').textContent = health.fps;
        
        // Update CPU meter
        document.getElementById('cpuFill').style.width = `${health.cpu}%`;
        document.getElementById('memoryFill').style.width = `${health.memory}%`;
    }
    
    updateAlerts(alerts) {
        const container = document.getElementById('alertList');
        if (!container) return;
        
        container.innerHTML = alerts.map(alert => `
            <div class="alert-item ${alert.severity}">
                <div class="alert-time">${alert.timestamp}</div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-type">${alert.type}</div>
            </div>
        `).join('');
    }
    
    updateCharts(data) {
        const timestamp = new Date().toLocaleTimeString();
        
        // Update threat timeline
        this.charts.threatTimeline.data.labels.push(timestamp);
        if (this.charts.threatTimeline.data.labels.length > 20) {
            this.charts.threatTimeline.data.labels.shift();
        }
        
        data.objects.forEach((obj, index) => {
            if (this.charts.threatTimeline.data.datasets[index]) {
                this.charts.threatTimeline.data.datasets[index].data.push(obj.threatScore);
                if (this.charts.threatTimeline.data.datasets[index].data.length > 20) {
                    this.charts.threatTimeline.data.datasets[index].data.shift();
                }
            }
        });
        
        this.charts.threatTimeline.update();
        
        // Update velocity chart
        this.charts.velocity.data.datasets[0].data = data.objects.map(obj => 
            Math.sqrt(obj.vx**2 + obj.vy**2)
        );
        this.charts.velocity.update();
    }
    
    showObjectDetails(objectId) {
        const object = this.data.objects.find(obj => obj.id === objectId);
        if (!object) return;
        
        // Create modal with object details
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <h2>Object #${object.id} Details</h2>
                <div class="object-details-full">
                    <div class="detail-section">
                        <h3>Position & Movement</h3>
                        <p>X: ${object.x.toFixed(2)} cm</p>
                        <p>Y: ${object.y.toFixed(2)} cm</p>
                        <p>Velocity X: ${object.vx.toFixed(2)} cm/s</p>
                        <p>Velocity Y: ${object.vy.toFixed(2)} cm/s</p>
                        <p>Speed: ${Math.sqrt(object.vx**2 + object.vy**2).toFixed(2)} cm/s</p>
                    </div>
                    <div class="detail-section">
                        <h3>Threat Assessment</h3>
                        <p>Threat Score: ${object.threatScore.toFixed(0)}%</p>
                        <p>Threat Level: ${object.threatLevel}</p>
                        <p>Confidence: ${(object.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div class="detail-section">
                        <h3>Sensor Readings</h3>
                        <p>Sensor 1: ${object.sensorReadings.s1.toFixed(1)} cm</p>
                        <p>Sensor 2: ${object.sensorReadings.s2.toFixed(1)} cm</p>
                        <p>Sensor 3: ${object.sensorReadings.s3.toFixed(1)} cm</p>
                    </div>
                </div>
                <canvas id="objectTrajectory_${object.id}" width="400" height="200"></canvas>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Draw trajectory
        this.drawObjectTrajectory(object.id);
    }
    
    drawObjectTrajectory(objectId) {
        // Implementation for trajectory visualization
        console.log(`Drawing trajectory for object ${objectId}`);
    }
    
    getThreatLevel(score) {
        if (score >= this.config.alertThresholds.critical) return 'CRITICAL';
        if (score >= this.config.alertThresholds.high) return 'HIGH';
        if (score >= this.config.alertThresholds.medium) return 'MEDIUM';
        if (score >= this.config.alertThresholds.low) return 'LOW';
        return 'NEGLIGIBLE';
    }
    
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours}h ${minutes}m ${secs}s`;
    }
    
    exportTrackingData() {
        const dataStr = JSON.stringify(this.data, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tracking_data_${Date.now()}.json`;
        a.click();
    }
    
    clearHistory() {
        this.data.history = [];
        this.charts.threatTimeline.data.labels = [];
        this.charts.threatTimeline.data.datasets.forEach(ds => ds.data = []);
        this.charts.threatTimeline.update();
    }
}

// Initialize dashboard
const dashboard = new AdvancedDashboard();

// ==================== BEHAVIOR ANALYSIS INTEGRATION ====================

class BehaviorIntegration {
    constructor() {
        this.behaviors = new Map();
        this.currentObjectId = 1;
        this.updateInterval = setInterval(() => this.updateBehaviorDisplay(), 500);
    }
    
    updateBehaviorDisplay() {
        const obj = objects.find(o => o.id === this.currentObjectId);
        if (!obj) return;
        
        // Simulate AI behavior analysis (in real app, this comes from Python)
        const behavior = this.analyzeBehavior(obj);
        
        // Update UI
        document.getElementById('primaryBehavior').textContent = behavior.primary;
        document.getElementById('behaviorProbability').textContent = 
            Math.round(behavior.confidence * 100) + '%';
        document.getElementById('behaviorMeter').style.width = 
            (behavior.confidence * 100) + '%';
        document.getElementById('behaviorColor').style.backgroundColor = behavior.color;
        document.getElementById('behaviorDescription').textContent = behavior.description;
        
        // Update feature values
        document.getElementById('behaviorSpeed').textContent = 
            behavior.features.speed.toFixed(1) + ' cm/s';
        document.getElementById('behaviorDirection').textContent = 
            Math.round(behavior.features.direction_change) + '°';
        document.getElementById('behaviorConsistency').textContent = 
            Math.round(behavior.features.consistency) + '%';
        document.getElementById('behaviorStationary').textContent = 
            Math.round(behavior.features.stationary) + '%';
        
        // Update all behaviors list
        const allBehaviorsDiv = document.getElementById('allBehaviors');
        allBehaviorsDiv.innerHTML = '';
        
        Object.entries(behavior.all_behaviors).forEach(([name, prob]) => {
            if (name === behavior.primary) return;
            
            const row = document.createElement('div');
            row.className = 'data-row';
            row.innerHTML = `
                <span style="color: #8b95b0;">${name}</span>
                <span style="color: #ffffff;">${Math.round(prob * 100)}%</span>
            `;
            allBehaviorsDiv.appendChild(row);
        });
        
        // Update interactions
        this.updateInteractions(obj);
    }
    
    analyzeBehavior(obj) {
        // Calculate behavior features
        const speed = Math.sqrt(obj.vx**2 + obj.vy**2);
        const distToCenter = Math.sqrt((obj.x - 50)**2 + (obj.y - 50)**2);
        
        // Determine behavior based on movement patterns
        let primary = 'normal';
        let confidence = 0.7;
        let color = '#00ff88';
        let description = 'Normal movement pattern';
        
        if (speed < 2 && distToCenter < 30) {
            primary = 'loitering';
            confidence = 0.85;
            color = '#ffaa00';
            description = 'Object lingering in same area. Potential surveillance activity.';
        } else if (speed > 15 && distToCenter < 40) {
            primary = 'rapid_approach';
            confidence = 0.9;
            color = '#ff4444';
            description = 'High-speed approach toward restricted zone. Immediate attention required.';
        } else if (Math.abs(obj.vx) > 10 && Math.abs(obj.vy) > 10) {
            primary = 'evasive_maneuvers';
            confidence = 0.8;
            color = '#ff6600';
            description = 'Erratic movement pattern. Attempting to avoid detection.';
        } else if (obj.x < 20 || obj.x > 80 || obj.y < 20 || obj.y > 80) {
            primary = 'patrolling';
            confidence = 0.75;
            color = '#ffaa00';
            description = 'Systematic movement along boundary. Perimeter scanning.';
        }
        
        // Calculate all behavior probabilities
        const all_behaviors = {
            'normal': 0.3,
            'loitering': 0.2,
            'rapid_approach': 0.1,
            'evasive_maneuvers': 0.1,
            'patrolling': 0.1,
            'following': 0.1,
            'waiting': 0.1
        };
        
        // Boost the primary behavior
        all_behaviors[primary] = confidence;
        
        // Normalize
        const total = Object.values(all_behaviors).reduce((a, b) => a + b, 0);
        Object.keys(all_behaviors).forEach(key => {
            all_behaviors[key] /= total;
        });
        
        return {
            primary: primary.toUpperCase(),
            confidence: all_behaviors[primary],
            color: color,
            description: description,
            all_behaviors: all_behaviors,
            features: {
                speed: speed,
                direction_change: Math.abs(Math.atan2(obj.vy, obj.vx)) * 180 / Math.PI,
                consistency: 70 + Math.random() * 20,
                stationary: speed < 2 ? 80 : 20
            }
        };
    }
    
    updateInteractions(obj) {
        const interactionDiv = document.getElementById('interactionDisplay');
        
        // Find nearby objects
        const nearby = objects.filter(o => {
            if (o.id === obj.id) return false;
            const dist = Math.sqrt((o.x - obj.x)**2 + (o.y - obj.y)**2);
            return dist < 30;
        });
        
        if (nearby.length === 0) {
            interactionDiv.innerHTML = `
                <div style="text-align: center; color: #8b95b0; padding: 20px;">
                    No interactions detected
                </div>
            `;
            return;
        }
        
        let html = '';
        nearby.forEach(other => {
            const dist = Math.sqrt((other.x - obj.x)**2 + (other.y - obj.y)**2);
            
            // Determine interaction type
            let interaction = 'nearby';
            let color = '#8b95b0';
            
            if (dist < 10) {
                interaction = 'meeting';
                color = '#ffaa00';
            } else if (dist < 20 && Math.abs(obj.vx - other.vx) < 2) {
                interaction = 'following';
                color = '#ff6600';
            }
            
            html += `
                <div style="display: flex; justify-content: space-between; padding: 8px; background: #0f1625; border-radius: 5px; margin-bottom: 5px;">
                    <div>
                        <span style="color: #00ff88;">Object ${other.id}</span>
                        <span style="color: ${color}; margin-left: 10px;">${interaction}</span>
                    </div>
                    <div style="color: #8b95b0;">${dist.toFixed(1)} cm</div>
                </div>
            `;
        });
        
        interactionDiv.innerHTML = html;
    }
    
    setCurrentObject(id) {
        this.currentObjectId = id;
    }
}

// Initialize
const behaviorIntegration = new BehaviorIntegration();

