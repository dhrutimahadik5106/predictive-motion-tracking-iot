/**
 * CONFIGURABLE MULTI-SENSOR TRACKER
 * Arduino UNO Code with Full Configuration Options
 * 
 * Features:
 * - 3 Ultrasonic Sensors (HC-SR04)
 * - 3 Servo Motors
 * - Configurable parameters via Serial
 * - Real-time data output
 * - Calibration mode
 */

#include <Servo.h>
#include <SoftwareSerial.h>

// ==================== PIN DEFINITIONS ====================
// Sensor 1 (Red)
#define TRIG1 9
#define ECHO1 8
#define SERVO1 10

// Sensor 2 (Green)
#define TRIG2 6
#define ECHO2 7
#define SERVO2 5

// Sensor 3 (Blue)
#define TRIG3 4
#define ECHO3 3
#define SERVO3 2

// LED Indicators
#define LED_RED 13
#define LED_GREEN 12
#define LED_BLUE 11

// ==================== CONFIGURABLE PARAMETERS ====================
// These can be changed via Serial commands
struct Config {
  // Scan parameters
  int scanMinAngle = 0;        // Minimum servo angle
  int scanMaxAngle = 180;       // Maximum servo angle
  int scanStep = 5;             // Step size in degrees
  int scanDelay = 50;           // Delay between steps (ms)
  
  // Detection parameters
  int maxRange = 200;           // Maximum detection range (cm)
  int minRange = 2;             // Minimum detection range (cm)
  int detectionThreshold = 20;   // Object detection threshold (cm)
  
  // Filter parameters
  int medianFilterSize = 3;      // Median filter window
  float kalmanQ = 0.1;          // Process noise
  float kalmanR = 5.0;          // Measurement noise
  
  // Output format
  bool outputJSON = true;        // JSON or CSV output
  int baudRate = 115200;         // Serial baud rate
  
  // Sensor positions for triangulation
  float sensor1X = 0.0;
  float sensor1Y = 0.0;
  float sensor2X = 100.0;
  float sensor2Y = 0.0;
  float sensor3X = 50.0;
  float sensor3Y = 86.6;
  
  // Calibration offsets
  int servo1Offset = 0;
  int servo2Offset = 0;
  int servo3Offset = 0;
  
  // Detection zones
  bool enableZone1 = true;
  int zone1X = 50;
  int zone1Y = 50;
  int zone1Radius = 20;
  
  bool enableZone2 = false;
  int zone2X1 = 20;
  int zone2Y1 = 20;
  int zone2X2 = 40;
  int zone2Y2 = 40;
};

// ==================== GLOBAL VARIABLES ====================
Config config;
Servo servo1, servo2, servo3;

// Kalman filter variables for each sensor
struct KalmanFilter {
  float Q;  // Process noise covariance
  float R;  // Measurement noise covariance
  float P;  // Estimation error covariance
  float K;  // Kalman gain
  float X;  // Value
};

KalmanFilter kalman1, kalman2, kalman3;

// Moving average buffers
const int MAX_HISTORY = 10;
float distHistory1[MAX_HISTORY];
float distHistory2[MAX_HISTORY];
float distHistory3[MAX_HISTORY];
int historyIndex = 0;

// System state
bool calibrated = false;
bool scanning = true;
int currentAngle = 0;
int scanDirection = 1;
unsigned long lastScanTime = 0;
unsigned long lastOutputTime = 0;

// ==================== SETUP ====================
void setup() {
  // Initialize serial
  Serial.begin(config.baudRate);
  
  // Initialize pins
  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);
  pinMode(TRIG3, OUTPUT);
  pinMode(ECHO3, INPUT);
  
  // Initialize LEDs
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  
  // Initialize servos
  servo1.attach(SERVO1);
  servo2.attach(SERVO2);
  servo3.attach(SERVO3);
  
  // Initialize Kalman filters
  initKalmanFilter(&kalman1, config.kalmanQ, config.kalmanR);
  initKalmanFilter(&kalman2, config.kalmanQ, config.kalmanR);
  initKalmanFilter(&kalman3, config.kalmanQ, config.kalmanR);
  
  // Initialize history buffers
  for (int i = 0; i < MAX_HISTORY; i++) {
    distHistory1[i] = 0;
    distHistory2[i] = 0;
    distHistory3[i] = 0;
  }
  
  // Print startup message
  Serial.println(F("{\"status\":\"initialized\",\"message\":\"Multi-Sensor Tracker Ready\"}"));
  Serial.println(F("{\"prompt\":\"Enter 'help' for commands\"}"));
  
  // Blink LEDs to indicate ready
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_BLUE, HIGH);
  delay(500);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
}

// ==================== MAIN LOOP ====================
void loop() {
  // Check for serial commands
  if (Serial.available()) {
    processCommand();
  }
  
  if (scanning) {
    performScan();
  }
  
  // Output data at regular interval
  if (millis() - lastOutputTime > 100) {  // 10Hz output
    outputData();
    lastOutputTime = millis();
  }
}

// ==================== SCANNING FUNCTION ====================
void performScan() {
  unsigned long now = millis();
  if (now - lastScanTime < config.scanDelay) {
    return;
  }
  lastScanTime = now;
  
  // Move servos to current angle (with offsets)
  servo1.write(currentAngle + config.servo1Offset);
  servo2.write(currentAngle + config.servo2Offset);
  servo3.write(currentAngle + config.servo3Offset);
  
  // Read all sensors
  float dist1 = readUltrasonic(TRIG1, ECHO1);
  float dist2 = readUltrasonic(TRIG2, ECHO2);
  float dist3 = readUltrasonic(TRIG3, ECHO3);
  
  // Apply Kalman filter
  dist1 = updateKalman(&kalman1, dist1);
  dist2 = updateKalman(&kalman2, dist2);
  dist3 = updateKalman(&kalman3, dist3);
  
  // Apply median filter
  dist1 = medianFilter(dist1, distHistory1);
  dist2 = medianFilter(dist2, distHistory2);
  dist3 = medianFilter(dist3, distHistory3);
  
  // Update history
  distHistory1[historyIndex] = dist1;
  distHistory2[historyIndex] = dist2;
  distHistory3[historyIndex] = dist3;
  historyIndex = (historyIndex + 1) % MAX_HISTORY;
  
  // Update angle for next scan
  currentAngle += scanDirection * config.scanStep;
  
  // Reverse direction at limits
  if (currentAngle >= config.scanMaxAngle) {
    currentAngle = config.scanMaxAngle;
    scanDirection = -1;
  } else if (currentAngle <= config.scanMinAngle) {
    currentAngle = config.scanMinAngle;
    scanDirection = 1;
  }
  
  // Update LEDs based on detections
  updateLEDs(dist1, dist2, dist3);
}

// ==================== ULTRASONIC READING ====================
float readUltrasonic(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, 30000);  // Timeout after 30ms
  
  if (duration == 0) {
    return config.maxRange + 1;  // Out of range
  }
  
  float distance = duration * 0.034 / 2;
  
  // Apply range limits
  if (distance < config.minRange) distance = config.minRange;
  if (distance > config.maxRange) distance = config.maxRange;
  
  return distance;
}

// ==================== KALMAN FILTER FUNCTIONS ====================
void initKalmanFilter(KalmanFilter* kf, float q, float r) {
  kf->Q = q;
  kf->R = r;
  kf->P = 1.0;
  kf->X = 0;
}

float updateKalman(KalmanFilter* kf, float measurement) {
  // Prediction update
  kf->P = kf->P + kf->Q;
  
  // Measurement update
  kf->K = kf->P / (kf->P + kf->R);
  kf->X = kf->X + kf->K * (measurement - kf->X);
  kf->P = (1 - kf->K) * kf->P;
  
  return kf->X;
}

// ==================== MEDIAN FILTER ====================
float medianFilter(float newValue, float* history) {
  float temp[MAX_HISTORY];
  memcpy(temp, history, sizeof(float) * MAX_HISTORY);
  
  // Simple bubble sort for small array
  for (int i = 0; i < MAX_HISTORY - 1; i++) {
    for (int j = 0; j < MAX_HISTORY - i - 1; j++) {
      if (temp[j] > temp[j + 1]) {
        float t = temp[j];
        temp[j] = temp[j + 1];
        temp[j + 1] = t;
      }
    }
  }
  
  return temp[MAX_HISTORY / 2];
}

// ==================== TRIANGULATION ====================
void calculatePosition(float d1, float d2, float d3, float* x, float* y) {
  // Triangulation using 3 sensor positions
  // Sensor 1: (s1x, s1y)
  // Sensor 2: (s2x, s2y)  
  // Sensor 3: (s3x, s3y)
  
  float A = 2 * (config.sensor2X - config.sensor1X);
  float B = 2 * (config.sensor2Y - config.sensor1Y);
  float C = d1*d1 - d2*d2 + config.sensor2X*config.sensor2X - config.sensor1X*config.sensor1X + 
            config.sensor2Y*config.sensor2Y - config.sensor1Y*config.sensor1Y;
  
  float D = 2 * (config.sensor3X - config.sensor2X);
  float E = 2 * (config.sensor3Y - config.sensor2Y);
  float F = d2*d2 - d3*d3 + config.sensor3X*config.sensor3X - config.sensor2X*config.sensor2X +
            config.sensor3Y*config.sensor3Y - config.sensor2Y*config.sensor2Y;
  
  // Solve linear equations
  float denominator = A*E - B*D;
  
  if (abs(denominator) < 0.001) {
    *x = -1;
    *y = -1;
    return;
  }
  
  *x = (C*E - B*F) / denominator;
  *y = (A*F - C*D) / denominator;
  
  // Validate result
  if (*x < 0 || *x > 100 || *y < 0 || *y > 100 || isnan(*x) || isnan(*y)) {
    *x = -1;
    *y = -1;
  }
}

// ==================== LED INDICATORS ====================
void updateLEDs(float d1, float d2, float d3) {
  // Red LED - Sensor 1 detection
  if (d1 < config.detectionThreshold) {
    digitalWrite(LED_RED, HIGH);
  } else {
    digitalWrite(LED_RED, LOW);
  }
  
  // Green LED - Sensor 2 detection
  if (d2 < config.detectionThreshold) {
    digitalWrite(LED_GREEN, HIGH);
  } else {
    digitalWrite(LED_GREEN, LOW);
  }
  
  // Blue LED - Sensor 3 detection
  if (d3 < config.detectionThreshold) {
    digitalWrite(LED_BLUE, HIGH);
  } else {
    digitalWrite(LED_BLUE, LOW);
  }
}

// ==================== THREAT ASSESSMENT ====================
int calculateThreatLevel(float x, float y, float d1, float d2, float d3) {
  int threat = 0;
  
  // Factor 1: Distance to restricted zone
  if (config.enableZone1) {
    float distToZone = sqrt(pow(x - config.zone1X, 2) + pow(y - config.zone1Y, 2));
    if (distToZone < config.zone1Radius) {
      threat += 50 * (1 - distToZone / config.zone1Radius);
    }
  }
  
  // Factor 2: Multiple sensors detecting (indicates larger object)
  int sensorsDetecting = 0;
  if (d1 < config.detectionThreshold) sensorsDetecting++;
  if (d2 < config.detectionThreshold) sensorsDetecting++;
  if (d3 < config.detectionThreshold) sensorsDetecting++;
  
  threat += sensorsDetecting * 10;
  
  // Factor 3: Close proximity
  if (d1 < 20 || d2 < 20 || d3 < 20) {
    threat += 30;
  }
  
  return min(100, threat);
}

// ==================== DATA OUTPUT ====================
void outputData() {
  if (config.outputJSON) {
    outputJSON();
  } else {
    outputCSV();
  }
}

void outputJSON() {
  float x, y;
  
  // Get latest filtered distances
  float d1 = distHistory1[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  float d2 = distHistory2[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  float d3 = distHistory3[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  
  // Calculate position if all sensors have valid readings
  if (d1 < config.maxRange && d2 < config.maxRange && d3 < config.maxRange) {
    calculatePosition(d1, d2, d3, &x, &y);
  } else {
    x = -1;
    y = -1;
  }
  
  // Calculate threat level
  int threat = calculateThreatLevel(x, y, d1, d2, d3);
  
  // Build JSON string
  Serial.print(F("{\"t\":"));
  Serial.print(millis());
  Serial.print(F(",\"a\":"));
  Serial.print(currentAngle);
  Serial.print(F(",\"s1\":"));
  Serial.print(d1, 1);
  Serial.print(F(",\"s2\":"));
  Serial.print(d2, 1);
  Serial.print(F(",\"s3\":"));
  Serial.print(d3, 1);
  
  if (x > 0 && y > 0) {
    Serial.print(F(",\"x\":"));
    Serial.print(x, 1);
    Serial.print(F(",\"y\":"));
    Serial.print(y, 1);
  }
  
  Serial.print(F(",\"th\":"));
  Serial.print(threat);
  Serial.println(F("}"));
}

void outputCSV() {
  float d1 = distHistory1[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  float d2 = distHistory2[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  float d3 = distHistory3[(historyIndex - 1 + MAX_HISTORY) % MAX_HISTORY];
  
  Serial.print(millis());
  Serial.print(F(","));
  Serial.print(currentAngle);
  Serial.print(F(","));
  Serial.print(d1, 1);
  Serial.print(F(","));
  Serial.print(d2, 1);
  Serial.print(F(","));
  Serial.print(d3, 1);
  Serial.println();
}

// ==================== COMMAND PROCESSING ====================
void processCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  
  if (command == "help") {
    printHelp();
  }
  else if (command == "status") {
    printStatus();
  }
  else if (command == "start") {
    scanning = true;
    Serial.println(F("{\"status\":\"scanning_started\"}"));
  }
  else if (command == "stop") {
    scanning = false;
    Serial.println(F("{\"status\":\"scanning_stopped\"}"));
  }
  else if (command == "calibrate") {
    calibrateSensors();
  }
  else if (command.startsWith("set ")) {
    setParameter(command);
  }
  else if (command == "save") {
    saveConfig();
  }
  else if (command == "load") {
    loadConfig();
  }
  else if (command == "default") {
    loadDefaultConfig();
  }
  else if (command == "test") {
    runDiagnostics();
  }
  else {
    Serial.print(F("{\"error\":\"Unknown command: "));
    Serial.print(command);
    Serial.println(F("\"}"));
  }
}

void printHelp() {
  Serial.println(F("{"));