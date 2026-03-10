/**
 * HEATMAP GENERATOR
 * Patent Feature: Real-time threat and activity heatmap visualization
 */

class HeatmapGenerator {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.data = [];
        this.config = {
            resolution: 50, // Grid resolution
            blurRadius: 15,
            maxIntensity: 100,
            colorScheme: 'threat', // 'threat', 'activity', 'confidence'
            updateRate: 200 // ms
        };
        
        this.init();
    }
    
    init() {
        this.canvas = document.getElementById('heatmapCanvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.setupControls();
        this.startUpdates();
    }
    
    setupControls() {
        // Resolution slider
        document.getElementById('heatmapResolution')?.addEventListener('input', (e) => {
            this.config.resolution = parseInt(e.target.value);
            document.getElementById('resolutionValue').textContent = e.target.value;
            this.generateHeatmap();
        });
        
        // Blur slider
        document.getElementById('heatmapBlur')?.addEventListener('input', (e) => {
            this.config.blurRadius = parseInt(e.target.value);
            document.getElementById('blurValue').textContent = e.target.value;
            this.generateHeatmap();
        });
        
        // Color scheme selector
        document.getElementById('colorScheme')?.addEventListener('change', (e) => {
            this.config.colorScheme = e.target.value;
            this.generateHeatmap();
        });
        
        // Export button
        document.getElementById('exportHeatmap')?.addEventListener('click', () => {
            this.exportHeatmap();
        });
    }
    
    startUpdates() {
        setInterval(() => {
            if (window.dashboard && window.dashboard.data) {
                this.updateData(window.dashboard.data.objects);
            }
        }, this.config.updateRate);
    }
    
    updateData(objects) {
        // Convert objects to heatmap data points
        this.data = objects.map(obj => ({
            x: obj.x,
            y: obj.y,
            intensity: obj.threatScore,
            weight: obj.confidence
        }));
        
        this.generateHeatmap();
    }
    
    generateHeatmap() {
        if (!this.ctx) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        
        // Create temporary buffer for heatmap
        const buffer = document.createElement('canvas');
        buffer.width = width;
        buffer.height = height;
        const bufferCtx = buffer.getContext('2d');
        
        // Draw data points
        this.data.forEach(point => {
            const x = (point.x / 100) * width;
            const y = (point.y / 100) * height;
            const intensity = point.intensity / 100;
            const radius = this.config.blurRadius * (0.5 + intensity * 0.5);
            
            // Create radial gradient for each point
            const gradient = bufferCtx.createRadialGradient(x, y, 0, x, y, radius);
            
            if (this.config.colorScheme === 'threat') {
                // Threat-based coloring (red = high threat)
                gradient.addColorStop(0, `rgba(255, ${Math.floor(255 * (1 - intensity))}, ${Math.floor(255 * (1 - intensity))}, ${intensity})`);
            } else if (this.config.colorScheme === 'activity') {
                // Activity-based (blue = active)
                gradient.addColorStop(0, `rgba(${Math.floor(100 * intensity)}, ${Math.floor(200 * intensity)}, 255, ${intensity})`);
            } else {
                // Confidence-based (green = confident)
                gradient.addColorStop(0, `rgba(${Math.floor(255 * (1 - intensity))}, 255, ${Math.floor(255 * (1 - intensity))}, ${intensity})`);
            }
            
            gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            
            bufferCtx.fillStyle = gradient;
            bufferCtx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
        });
        
        // Apply blur for smoother heatmap
        this.ctx.filter = `blur(${this.config.blurRadius / 2}px)`;
        this.ctx.drawImage(buffer, 0, 0);
        this.ctx.filter = 'none';
        
        // Draw grid overlay
        this.drawGrid(width, height);
        
        // Draw sensor positions
        this.drawSensors(width, height);
        
        // Update statistics
        this.updateStatistics();
    }
    
    drawGrid(width, height) {
        const gridSize = width / this.config.resolution;
        
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(width, y);
            this.ctx.stroke();
        }
    }
    
    drawSensors(width, height) {
        const sensors = [
            { x: 30, y: 30, color: '#ff4444' },
            { x: 70, y: 30, color: '#00ff88' },
            { x: 50, y: 70, color: '#4444ff' }
        ];
        
        sensors.forEach(sensor => {
            const x = (sensor.x / 100) * width;
            const y = (sensor.y / 100) * height;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 8, 0, Math.PI * 2);
            this.ctx.fillStyle = sensor.color;
            this.ctx.fill();
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Sensor label
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.fillText('S', x - 4, y + 4);
        });
    }
    
    updateStatistics() {
        // Calculate heatmap statistics
        const stats = {
            totalIntensity: this.data.reduce((sum, p) => sum + p.intensity, 0),
            maxIntensity: Math.max(...this.data.map(p => p.intensity), 0),
            avgIntensity: this.data.length ? 
                this.data.reduce((sum, p) => sum + p.intensity, 0) / this.data.length : 0,
            hotZones: this.findHotZones()
        };
        
        // Update UI
        document.getElementById('peakIntensity').textContent = `${stats.maxIntensity.toFixed(0)}%`;
        document.getElementById('avgIntensity').textContent = `${stats.avgIntensity.toFixed(0)}%`;
        document.getElementById('hotZoneCount').textContent = stats.hotZones.length;
        
        // Draw hot zones
        this.drawHotZones(stats.hotZones);
    }
    
    findHotZones(threshold = 70) {
        // Simple clustering of high-intensity areas
        const hotZones = [];
        const processed = new Set();
        
        this.data.forEach((point, i) => {
            if (processed.has(i)) return;
            if (point.intensity < threshold) return;
            
            // Find nearby points
            const cluster = [point];
            processed.add(i);
            
            this.data.forEach((other, j) => {
                if (processed.has(j)) return;
                if (other.intensity < threshold) return;
                
                const distance = Math.sqrt(
                    Math.pow(point.x - other.x, 2) + 
                    Math.pow(point.y - other.y, 2)
                );
                
                if (distance < 15) {
                    cluster.push(other);
                    processed.add(j);
                }
            });
            
            if (cluster.length > 0) {
                const centerX = cluster.reduce((sum, p) => sum + p.x, 0) / cluster.length;
                const centerY = cluster.reduce((sum, p) => sum + p.y, 0) / cluster.length;
                const avgIntensity = cluster.reduce((sum, p) => sum + p.intensity, 0) / cluster.length;
                
                hotZones.push({
                    center: { x: centerX, y: centerY },
                    intensity: avgIntensity,
                    size: cluster.length
                });
            }
        });
        
        return hotZones;
    }
    
    drawHotZones(hotZones) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        hotZones.forEach(zone => {
            const x = (zone.center.x / 100) * width;
            const y = (zone.center.y / 100) * height;
            
            // Draw zone marker
            this.ctx.beginPath();
            this.ctx.arc(x, y, 20, 0, Math.PI * 2);
            this.ctx.strokeStyle = '#ff4444';
            this.ctx.lineWidth = 3;
            this.ctx.setLineDash([5, 5]);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            
            // Draw intensity label
            this.ctx.fillStyle = '#ff4444';
            this.ctx.font = 'bold 14px Arial';
            this.ctx.fillText(`${zone.intensity.toFixed(0)}%`, x - 20, y - 25);
        });
    }
    
    exportHeatmap() {
        // Create a composite image with heatmap and legend
        const exportCanvas = document.createElement('canvas');
        exportCanvas.width = this.canvas.width;
        exportCanvas.height = this.canvas.height + 50;
        const exportCtx = exportCanvas.getContext('2d');
        
        // Draw heatmap
        exportCtx.fillStyle = '#0a0f1a';
        exportCtx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
        exportCtx.drawImage(this.canvas, 0, 0);
        
        // Draw legend
        const gradient = exportCtx.createLinearGradient(50, this.canvas.height + 10, 250, this.canvas.height + 10);
        gradient.addColorStop(0, '#00ff88');
        gradient.addColorStop(0.5, '#ffaa00');
        gradient.addColorStop(1, '#ff4444');
        
        exportCtx.fillStyle = gradient;
        exportCtx.fillRect(50, this.canvas.height + 10, 200, 20);
        
        exportCtx.fillStyle = 'white';
        exportCtx.font = '12px Arial';
        exportCtx.fillText('Low', 10, this.canvas.height + 25);
        exportCtx.fillText('High', 260, this.canvas.height + 25);
        
        // Download
        const link = document.createElement('a');
        link.download = `heatmap_${Date.now()}.png`;
        link.href = exportCanvas.toDataURL();
        link.click();
    }
    
    getHeatmapData() {
        return {
            config: this.config,
            data: this.data,
            timestamp: Date.now(),
            statistics: {
                peakIntensity: Math.max(...this.data.map(p => p.intensity), 0),
                avgIntensity: this.data.length ? 
                    this.data.reduce((sum, p) => sum + p.intensity, 0) / this.data.length : 0,
                dataPoints: this.data.length
            }
        };
    }
}

// Initialize heatmap
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('heatmapCanvas')) {
        window.heatmapGenerator = new HeatmapGenerator();
    }
});