#include <SharpIR.h>
#include <NewPing.h>

#define SONAR_NUM 4      // Number of sensors.
#define MAX_DISTANCE 150 // Maximum distance (in cm) to ping.

NewPing sonar[SONAR_NUM] = {   // Sensor object array.
  NewPing(4, 5, MAX_DISTANCE), // back 
  NewPing(8, 9, MAX_DISTANCE), //right
  NewPing(6, 7, MAX_DISTANCE), //center
  NewPing(2, 3, MAX_DISTANCE) //left
};

int pingDistances[SONAR_NUM];
SharpIR sensorMiddleLeft(SharpIR::GP2Y0A41SK0F, A6 );
SharpIR sensorMiddleRight(SharpIR::GP2Y0A41SK0F, A4 );
SharpIR sensorBackLeft(SharpIR::GP2Y0A21YK0F, A5 );
SharpIR sensorBackRight(SharpIR::GP2Y0A21YK0F, A3 );

void setup() {
  Serial.begin(19200); // Open serial monitor at 19200 baud to see ping results.
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(8, OUTPUT);

  pinMode(3, INPUT);
  pinMode(5, INPUT);
  pinMode(7, INPUT);
  pinMode(9, INPUT);
  //pinMode(2, INPUT);
  //pinMode(3, INPUT);
  //pinMode(A0, INPUT);
  //pinMode(13, INPUT);
  //pinMode(A1, INPUT);
}

void loop() { 
  for (uint8_t i = 0; i < SONAR_NUM; i++) { // Loop through each sensor and display results.
    delay(30); // Wait 50ms between pings (about 20 pings/sec). 29ms should be the shortest delay between pings.
    pingDistances[i] = sonar[i].convert_cm(sonar[i].ping_median(1,MAX_DISTANCE));
  }
  Serial.print(pingDistances[0]);
  Serial.print(",");
  Serial.print(pingDistances[1]);
  Serial.print(",");
  Serial.print(pingDistances[2]);
  Serial.print(",");
  Serial.print(pingDistances[3]);
  Serial.print(",");
  Serial.print(sensorMiddleLeft.getDistance());
  Serial.print(",");
  Serial.print(sensorMiddleRight.getDistance());
  Serial.print(",");
  Serial.print(sensorBackLeft.getDistance());
  Serial.print(",");
  Serial.println(sensorBackRight.getDistance());
  
}

int getDistance(int trigPin, int echoPin) // returns the distance (cm)
{
long duration, distance;


digitalWrite(trigPin, LOW);
delayMicroseconds(10);
digitalWrite(trigPin, HIGH); // We send a 10us pulse
delayMicroseconds(100);
digitalWrite(trigPin, LOW);

duration = pulseIn(echoPin, HIGH, 15000); // We wait for the echo to come back, with a timeout of 20ms, which corresponds approximately to 3m

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

