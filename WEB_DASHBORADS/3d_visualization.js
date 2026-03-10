/**
 * 3D Visualization for Multi-Object Tracking
 * Uses Three.js for real-time rendering
 */

class Visualizer3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.objects = new Map();
        this.sensors = [];
        this.trails = new Map();
        this.trailLines = [];
        this.trailsEnabled = true;
        
        this.init();
    }
    
    init() {
        const container = document.getElementById('canvas-container');
        
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0f1a);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60, 
            container.clientWidth / container.clientHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(120, 80, 150);
        this.camera.lookAt(50, 0, 50);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Lighting
        this.setupLights();
        
        // Environment
        this.setupEnvironment();
        
        // Sensors
        this.createSensors();
        
        // Start animation
        this.animate();
        
        // Handle resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404060);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(100, 200, 100);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        
        const d = 150;
        directionalLight.shadow.camera.left = -d;
        directionalLight.shadow.camera.right = d;
        directionalLight.shadow.camera.top = d;
        directionalLight.shadow.camera.bottom = -d;
        directionalLight.shadow.camera.near = 1;
        directionalLight.shadow.camera.far = 300;
        
        this.scene.add(directionalLight);
        
        // Fill lights
        const fillLight1 = new THREE.PointLight(0x4466ff, 0.3);
        fillLight1.position.set(-50, 30, 100);
        this.scene.add(fillLight1);
        
        const fillLight2 = new THREE.PointLight(0xff6644, 0.3);
        fillLight2.position.set(150, 30, -50);
        this.scene.add(fillLight2);
    }
    
    setupEnvironment() {
        // Ground grid
        const gridHelper = new THREE.GridHelper(200, 20, 0x00ff88, 0x2a3248);
        gridHelper.position.y = 0;
        this.scene.add(gridHelper);
        
        // Ground plane
        const groundGeometry = new THREE.PlaneGeometry(200, 200);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x0a0f1a,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = 0.1;
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        // Restricted zone (center)
        const zoneGeometry = new THREE.CylinderGeometry(20, 20, 1, 32);
        const zoneMaterial = new THREE.MeshStandardMaterial({
            color: 0xff4444,
            transparent: true,
            opacity: 0.2,
            emissive: 0x330000
        });
        const zone = new THREE.Mesh(zoneGeometry, zoneMaterial);
        zone.position.set(50, 0.5, 50);
        zone.receiveShadow = true;
        this.scene.add(zone);
        
        // Zone border
        const borderGeometry = new THREE.TorusGeometry(20, 0.3, 16, 100);
        const borderMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xff4444,
            emissive: 0x440000
        });
        const border = new THREE.Mesh(borderGeometry, borderMaterial);
        border.rotation.x = Math.PI / 2;
        border.position.set(50, 1, 50);
        this.scene.add(border);
        
        // Corner markers
        const markerMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff88 });
        for (let x = 0; x <= 100; x += 100) {
            for (let z = 0; z <= 100; z += 100) {
                const marker = new THREE.Mesh(
                    new THREE.BoxGeometry(2, 2, 2),
                    markerMaterial
                );
                marker.position.set(x, 1, z);
                this.scene.add(marker);
            }
        }
    }
    
    createSensors() {
        const sensorPositions = [
            { x: 30, y: 0, z: 30, color: 0xff4444, label: 'S1' },
            { x: 70, y: 0, z: 30, color: 0x00ff88, label: 'S2' },
            { x: 50, y: 0, z: 70, color: 0x4444ff, label: 'S3' }
        ];
        
        sensorPositions.forEach((pos, index) => {
            // Base
            const baseGeo = new THREE.CylinderGeometry(4, 4, 2, 16);
            const baseMat = new THREE.MeshStandardMaterial({ color: 0x333333 });
            const base = new THREE.Mesh(baseGeo, baseMat);
            base.position.set(pos.x, 1, pos.z);
            base.castShadow = true;
            base.receiveShadow = true;
            this.scene.add(base);
            
            // Pole
            const poleGeo = new THREE.CylinderGeometry(1, 1, 8, 8);
            const poleMat = new THREE.MeshStandardMaterial({ color: pos.color });
            const pole = new THREE.Mesh(poleGeo, poleMat);
            pole.position.set(pos.x, 6, pos.z);
            pole.castShadow = true;
            pole.receiveShadow = true;
            this.scene.add(pole);
            
            // Head
            const headGeo = new THREE.SphereGeometry(2.5, 16, 16);
            const headMat = new THREE.MeshStandardMaterial({ 
                color: pos.color,
                emissive: pos.color,
                emissiveIntensity: 0.3
            });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.set(pos.x, 11, pos.z);
            head.castShadow = true;
            head.receiveShadow = true;
            this.scene.add(head);
            
            // Detection range (wireframe)
            const rangeGeo = new THREE.SphereGeometry(40, 16, 16);
            const rangeMat = new THREE.MeshPhongMaterial({
                color: pos.color,
                transparent: true,
                opacity: 0.1,
                wireframe: true
            });
            const range = new THREE.Mesh(rangeGeo, rangeMat);
            range.position.set(pos.x, 0, pos.z);
            this.scene.add(range);
            
            // Store sensor
            this.sensors.push({
                head: head,
                range: range,
                position: pos,
                pulseTime: 0
            });
        });
    }
    
    createObjectMesh(obj) {
        const group = new THREE.Group();
        
        // Determine color based on threat level
        let color;
        if (obj.threatLevel === 'HIGH') color = 0xff4444;
        else if (obj.threatLevel === 'MEDIUM') color = 0xffaa00;
        else color = 0x00ff88;
        
        // Different shapes for different types
        if (obj.type === 'intruder') {
            // Intruder - cone shape (threatening)
            const bodyGeo = new THREE.ConeGeometry(3, 8, 8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: color });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 4;
            body.castShadow = true;
            body.receiveShadow = true;
            group.add(body);
            
            // Spikes or warning indicators
            const spikeGeo = new THREE.ConeGeometry(1, 2, 6);
            const spikeMat = new THREE.MeshStandardMaterial({ color: 0xffaa00 });
            
            for (let i = 0; i < 4; i++) {
                const spike = new THREE.Mesh(spikeGeo, spikeMat);
                spike.position.set(
                    Math.cos(i * Math.PI/2) * 2,
                    7,
                    Math.sin(i * Math.PI/2) * 2
                );
                spike.rotation.x = 0.2;
                spike.rotation.z = i * Math.PI/2;
                spike.castShadow = true;
                group.add(spike);
            }
        } else {
            // Normal object - sphere with ring
            const bodyGeo = new THREE.SphereGeometry(3, 16, 16);
            const bodyMat = new THREE.MeshStandardMaterial({ color: color });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 3;
            body.castShadow = true;
            body.receiveShadow = true;
            group.add(body);
            
            // Orbiting ring
            const ringGeo = new THREE.TorusGeometry(4, 0.5, 8, 32);
            const ringMat = new THREE.MeshStandardMaterial({ color: color });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2;
            ring.rotation.z = Math.PI / 4;
            ring.position.y = 3;
            ring.castShadow = true;
            group.add(ring);
        }
        
        // Add ID label (using a small sphere with number - in real implementation use sprite)
        const labelGeo = new THREE.SphereGeometry(1, 6, 6);
        const labelMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
        const label = new THREE.Mesh(labelGeo, labelMat);
        label.position.y = 8;
        group.add(label);
        
        return group;
    }
    
    createTrail(objectId, x, z) {
        const points = [];
        for (let i = 0; i < 20; i++) {
            points.push(new THREE.Vector3(x, 0.5, z));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: 0x00ff88 });
        const line = new THREE.Line(geometry, material);
        
        this.scene.add(line);
        this.trailLines.push(line);
        this.trails.set(objectId, {
            line: line,
            points: points,
            maxLength: 20
        });
    }
    
    updateTrail(objectId, x, z) {
        const trail = this.trails.get(objectId);
        if (!trail) {
            this.createTrail(objectId, x, z);
            return;
        }
        
        // Add new point
        trail.points.push(new THREE.Vector3(x, 0.5, z));
        
        // Remove old points
        if (trail.points.length > trail.maxLength) {
            trail.points.shift();
        }
        
        // Update line geometry
        trail.line.geometry.dispose();
        trail.line.geometry = new THREE.BufferGeometry().setFromPoints(trail.points);
    }
    
    updateObjects(objects, sensors) {
        // Remove old objects
        this.objects.forEach((obj, id) => {
            if (!objects.find(o => o.id === id)) {
                this.scene.remove(obj);
                this.objects.delete(id);
                
                // Remove trail
                const trail = this.trails.get(id);
                if (trail) {
                    this.scene.remove(trail.line);
                    this.trails.delete(id);
                }
            }
        });
        
        // Update/create objects
        objects.forEach(obj => {
            if (!this.objects.has(obj.id)) {
                // Create new object
                const mesh = this.createObjectMesh(obj);
                mesh.position.set(obj.x, 0, obj.y);
                this.objects.set(obj.id, mesh);
                this.scene.add(mesh);
                
                // Create trail
                if (this.trailsEnabled) {
                    this.createTrail(obj.id, obj.x, obj.y);
                }
            } else {
                // Update existing object
                const mesh = this.objects.get(obj.id);
                
                // Smooth movement
                mesh.position.x += (obj.x - mesh.position.x) * 0.1;
                mesh.position.z += (obj.y - mesh.position.z) * 0.1;
                
                // Rotate based on velocity
                if (obj.vx && obj.vy) {
                    mesh.rotation.y = Math.atan2(obj.vx, obj.vy);
                }
                
                // Update trail
                if (this.trailsEnabled) {
                    this.updateTrail(obj.id, mesh.position.x, mesh.position.z);
                }
            }
        });
        
        // Animate sensors
        this.sensors.forEach(sensor => {
            sensor.pulseTime += 0.05;
            const scale = 1 + Math.sin(sensor.pulseTime) * 0.1;
            sensor.head.scale.set(scale, scale, scale);
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Animate sensors (pulse)
        this.sensors.forEach(sensor => {
            sensor.pulseTime += 0.03;
            const scale = 1 + Math.sin(sensor.pulseTime) * 0.1;
            sensor.head.scale.set(scale, scale, scale);
            
            // Rotate slowly
            sensor.head.rotation.y += 0.005;
        });
        
        this.renderer.render(this.scene, this.camera);
    }
    
    setCameraView(view) {
        switch(view) {
            case 'top':
                this.camera.position.set(50, 150, 50);
                break;
            case 'side':
                this.camera.position.set(200, 50, 50);
                break;
            case 'dynamic':
                this.camera.position.set(120, 80, 150);
                break;
        }
        this.camera.lookAt(50, 0, 50);
    }
    
    toggleTrails(enabled) {
        this.trailsEnabled = enabled;
        
        // Show/hide all trails
        this.trailLines.forEach(line => {
            line.visible = enabled;
        });
    }
    
    handleResize() {
        const container = document.getElementById('canvas-container');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
}

// Initialize 3D visualizer
document.addEventListener('DOMContentLoaded', () => {
    window.visualizer3D = new Visualizer3D();
});