// Arduino-SerialCommand - Version: Latest 
#include <SerialCommand.h>

#define pinMotorLEnable 3
#define pinMotorLIn1 4
#define pinMotorLIn2 5
#define pinMotorREnable 6
#define pinMotorRIn1 7
#define pinMotorRIn2 8

SerialCommand sCmd;     

void setup() {
    pinMode(pinMotorLEnable, OUTPUT);
    pinMode(pinMotorLIn1, OUTPUT);
    pinMode(pinMotorLIn2, OUTPUT);
    pinMode(pinMotorREnable, OUTPUT);
    pinMode(pinMotorRIn1, OUTPUT);
    pinMode(pinMotorRIn2, OUTPUT);
    
    Serial.begin(57600);

    // Setup callbacks for SerialCommand commands
    sCmd.addCommand("ID",           ID);
    sCmd.addCommand("L",    Drive_Motor_Left);
    sCmd.addCommand("R",    Drive_Motor_Right);    
    sCmd.addCommand("B",    Drive_Motors_Both);
    sCmd.setDefaultHandler(unrecognized);      // Handler for command that isn't matched  (says "What?")
}

void loop() {
  sCmd.readSerial();     // We don't do much, just process serial commands
}


void ID(){
  Serial.println("MotorsController");
}

int get_motor_speed(){
  char *arg;
  int motorSpeed;
  arg = sCmd.next();    // Get the next argument from the SerialCommand object buffer
  if (arg != NULL) {    // As long as it existed, take it
    return atoi(arg);
  }
  return 0;
}

void drive_motor(int pinIn1, int pinIn2, int pinEnable, int motorSpeed){
  if(motorSpeed==0){
      digitalWrite(pinIn1, LOW);
      digitalWrite(pinIn2, LOW);
      analogWrite(pinEnable, 0);          
  }
  else if(motorSpeed>0){
      digitalWrite(pinIn1, LOW);
      digitalWrite(pinIn2, HIGH);    
      analogWrite(pinEnable, motorSpeed);          
  }
  else{
      digitalWrite(pinIn1, HIGH);
      digitalWrite(pinIn2, LOW);    
      analogWrite(pinEnable, -motorSpeed);          
  }
}

void Drive_Motor_Left(){
  drive_motor(pinMotorLIn1, pinMotorLIn2, pinMotorLEnable, get_motor_speed());
}

void Drive_Motor_Right(){
  drive_motor(pinMotorRIn1, pinMotorRIn2, pinMotorREnable, get_motor_speed());
}

void Drive_Motors_Both(){
  int motorSpeed = get_motor_speed();
  drive_motor(pinMotorLIn1, pinMotorLIn2, pinMotorLEnable, motorSpeed);
  drive_motor(pinMotorRIn1, pinMotorRIn2, pinMotorREnable, motorSpeed);
}


// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command) {
  Serial.println("What?");
} 