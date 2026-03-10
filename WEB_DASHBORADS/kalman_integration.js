// // ==================== KALMAN FILTER INTEGRATION ====================

// class KalmanDisplay {
//     constructor() {
//         this.data = {
//             positions: [],
//             raw_measurements: [],
//             uncertainties: [],
//             gains: [],
//             innovations: []
//         };
        
//         this.initChart();
//         this.startUpdates();
//     }
    
//     initChart() {
//         const ctx = document.getElementById('kalmanComparisonChart').getContext('2d');
//         this.chart = new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: [],
//                 datasets: [
//                     {
//                         label: 'Raw Measurement',
//                         data: [],
//                         borderColor: '#ff4444',
//                         backgroundColor: 'transparent',
//                         borderDash: [5, 5],
//                         pointRadius: 2
//                     },
//                     {
//                         label: 'Kalman Filtered',
//                         data: [],
//                         borderColor: '#00ff88',
//                         backgroundColor: 'transparent',
//                         borderWidth: 2,
//                         pointRadius: 0
//                     },
//                     {
//                         label: 'Uncertainty (±)',
//                         data: [],
//                         borderColor: '#ffaa00',
//                         backgroundColor: 'rgba(255, 170, 0, 0.1)',
//                         fill: '+1',
//                         pointRadius: 0
//                     }
//                 ]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: {
//                     y: {
//                         min: 0,
//                         max: 100,
//                         grid: { color: '#2a3248' }
//                     }
//                 },
//                 plugins: {
//                     legend: { labels: { color: '#fff' } }
//                 }
//             }
//         });
//     }
    
//     updateKalmanData(objectId) {
//         // Simulate Kalman filter output
//         const time = Date.now() / 1000;
        
//         // Generate realistic Kalman data
//         const trueX = 50 + 30 * Math.sin(time * 0.1);
//         const rawX = trueX + (Math.random() - 0.5) * 4; // Noisy measurement
//         const filteredX = trueX + (Math.random() - 0.5) * 1; // Smoothed
        
//         const uncertainty = 1.5 + Math.sin(time) * 0.5;
//         const kalmanGain = 0.7 + Math.cos(time * 0.5) * 0.2;
//         const innovation = Math.abs(rawX - filteredX);
        
//         // Update display
//         document.getElementById('kalmanX').textContent = filteredX.toFixed(2);
//         document.getElementById('kalmanY').textContent = (50 + 20 * Math.cos(time * 0.12)).toFixed(2);
//         document.getElementById('kalmanVx').textContent = (3 * Math.cos(time * 0.1)).toFixed(2) + ' cm/s';
//         document.getElementById('kalmanVy').textContent = (-2.4 * Math.sin(time * 0.12)).toFixed(2) + ' cm/s';
//         document.getElementById('kalmanSpeed').textContent = 
//             Math.sqrt((3 * Math.cos(time * 0.1))**2 + (2.4 * Math.sin(time * 0.12))**2).toFixed(2) + ' cm/s';
        
//         document.getElementById('kalmanAx').textContent = (0.1 * Math.sin(time)).toFixed(2) + ' cm/s²';
//         document.getElementById('kalmanAy').textContent = (0.05 * Math.cos(time)).toFixed(2) + ' cm/s²';
//         document.getElementById('kalmanAccel').textContent = 
//             Math.sqrt((0.1 * Math.sin(time))**2 + (0.05 * Math.cos(time))**2).toFixed(2) + ' cm/s²';
        
//         document.getElementById('kalmanUncertainty').textContent = `±${uncertainty.toFixed(2)} cm`;
//         document.getElementById('uncertaintyMeter').style.width = (uncertainty / 5 * 100) + '%';
        
//         document.getElementById('kalmanGain').textContent = kalmanGain.toFixed(2);
//         document.getElementById('measurementTrust').textContent = Math.round(kalmanGain * 100) + '%';
//         document.getElementById('predictionTrust').textContent = Math.round((1 - kalmanGain) * 100) + '%';
        
//         document.getElementById('kalmanInnovation').textContent = innovation.toFixed(2) + ' cm';
        
//         // Update predictions
//         const predictionsDiv = document.getElementById('kalmanPredictions');
//         predictionsDiv.innerHTML = '';
        
//         for (let i = 1; i <= 5; i++) {
//             const predX = filteredX + (3 * Math.cos(time * 0.1)) * i * 0.2;
//             const predY = (50 + 20 * Math.cos((time + i*0.2) * 0.12));
//             const predUncertainty = uncertainty * (1 + i * 0.2);
            
//             predictionsDiv.innerHTML += `
//                 <div style="background: #0f1625; padding: 5px; border-radius: 4px; text-align: center;">
//                     <div style="font-size: 10px; color: #8b95b0;">Step ${i}</div>
//                     <div style="font-size: 11px; color: #00ff88;">${predX.toFixed(0)}</div>
//                     <div style="font-size: 11px; color: #00ff88;">${predY.toFixed(0)}</div>
//                     <div style="font-size: 8px; color: #8b95b0;">±${predUncertainty.toFixed(1)}</div>
//                 </div>
//             `;
//         }
        
//         // Update chart
//         this.chart.data.labels.push('');