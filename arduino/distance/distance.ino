#define SONAR_NUM 3      // Number of sensors.
int pingDistances[SONAR_NUM];

void setup() {
  Serial.begin(19200); // Open serial monitor at 19200 baud to see ping results.
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(6, OUTPUT);
  
  pinMode(3, INPUT);
  pinMode(5, INPUT);
  pinMode(7, INPUT);
}

void loop() { 
  long start_time = millis();
  pingDistances[0] = getDistance(6,7);
  pingDistances[1] = getDistance(4,5);
  pingDistances[2] = getDistance(2,3);
  //for (uint8_t i = 0; i < SONAR_NUM; i++) { // Loop through each sensor and display results.
    //delay(50); // Wait 50ms between pings (about 20 pings/sec). 29ms should be the shortest delay between pings.
    //pingDistances[i] = sonar[i].convert_cm(sonar[i].ping_median(1,MAX_DISTANCE));
  //}
  Serial.print(pingDistances[0]);
  Serial.print(",");
  Serial.print(pingDistances[1]);
  Serial.print(",");
  Serial.println(pingDistances[2]);
  delay(30-millis()+start_time);
}

int getDistance(int trigPin, int echoPin) // returns the distance (cm)
{
long duration, distance;


digitalWrite(trigPin, LOW);
delayMicroseconds(10);
digitalWrite(trigPin, HIGH); // We send a 10us pulse
delayMicroseconds(120);
digitalWrite(trigPin, LOW);

duration = pulseIn(echoPin, HIGH, 20000); // We wait for the echo to come back, with a timeout of 20ms, which corresponds approximately to 3m

// pulseIn will only return 0 if it timed out. (or if echoPin was already to 1, but it should not happen)
if(duration == 0) // If we timed out
{
pinMode(echoPin, OUTPUT); // Then we set echo pin to output mode
digitalWrite(echoPin, LOW); // We send a LOW pulse to the echo pin
delayMicroseconds(200);
pinMode(echoPin, INPUT); // And finaly we come back to input mode
}

distance = (duration/2) / 29.1; // We calculate the distance (sound speed in air is aprox. 291m/s), /2 because of the pulse going and coming
return distance; //We return the result. Here you can find a 0 if we timed out
}
