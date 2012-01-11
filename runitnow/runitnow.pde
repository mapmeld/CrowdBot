#include <WProgram.h>
/* Data Streamer
  streams light sensor value to CrowdBot
  target light is red LED with variable analog value */
int lightSense;
int lightCycle = 1;
void setup(){
  pinMode(10, OUTPUT);
  Serial.begin(9600);
  randomSeed( analogRead(0) );
}
void loop(){
  // set the light LED to a random value every 4 seconds
  if(lightCycle % 5 == 0){
    lightCycle = 1;
    analogWrite(10, random(20,250) );
  }
  else{
    lightCycle = lightCycle + 1;
  }
  // read the light sensor every second
  lightSense = analogRead(3);
  Serial.println( lightSense );
  delay(1000);
}

extern "C" void __cxa_pure_virtual(){
  while (1);
}