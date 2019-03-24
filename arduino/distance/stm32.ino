/*
 * getDistance
 *
 * Example of using SharpIR library to calculate the distance beetween the sensor and an obstacle
 *
 * Created by Giuseppe Masino, 15 June 2016
 *
 * -----------------------------------------------------------------------------------
 *
 * Things that you need:
 * - Arduino
 * - A Sharp IR Sensor
 *
 *
 * The circuit:
 * - Arduino 5V -> Sensor's pin 1 (Vcc)
 * - Arduino GND -> Sensor's pin 2 (GND)
 * - Arduino pin A0 -> Sensor's pin 3 (Output)
 *
 *
 * See the Sharp sensor datasheet for the pin reference, the pin configuration is the same for all models.
 * There is the datasheet for the model GP2Y0A41SK0F:
 *
 * http://www.robotstore.it/open2b/var/product-files/78.pdf
 *
 */
void setup()
{
  Serial.begin( 57600 ); //Enable the serial comunication
}

void loop()
{
  delay(10);  Serial.print( get_distance(0)); //Print the value to the serial monitor
  Serial.print(","); //Print the value to the serial monitor
  Serial.print( get_distance(1)); //Print the value to the serial monitor
  Serial.print(","); //Print the value to the serial monitor
  Serial.println( get_distance(2)); //Print the value to the serial monitor
}

int get_distance(int pin){
      int distance = 12632/(analogRead(pin)*0.38-20);
      if(distance > 100) return 1000;
      else if(distance < 6) return 5;
      else return distance;
}
