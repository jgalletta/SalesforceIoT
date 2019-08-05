// Ultrasonic Serial Data to Python
// Created by: Jack Galletta, Summer 2019
// jgalletta@salesforce.com


// assigning pins to sensor
const int trigPin = 7;
const int echoPin = 6;
const int ledPin = 13;

// creating global vars
long duration;
int distance;
int count;

void setup() {
  // configuring pins and baud rate
  pinMode(trigPin,OUTPUT);
  pinMode(echoPin,INPUT);
  pinMode(ledPin,OUTPUT);
    Serial.begin(9600);
}

void loop() {

  // set trigger to low and send out 10us pulse to begin detection
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // stores echo pulse length in duration
  duration = pulseIn(echoPin, HIGH);

  // calculates distance based on speed of sound
  distance = duration*0.034/2;

  // adding LED functionality
  if (distance <= 10){
    count += 1;
    if(count%80 == 0){
      digitalWrite(ledPin, HIGH);
      delay(160);
      digitalWrite(ledPin, LOW);
    }
  }
  // sends distance variable through serial port: '/dev/cu.usbmodem14201'
  Serial.println(distance);
}
