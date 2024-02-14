#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

#define SERVO_SWEEPS 50
#define CAR_STEPS 10
#define car_distance 1900

#define STARTING_ANGLE 120
#define PERIOD 2000
#define PI 3.14159
double angles[SERVO_SWEEPS];

int enable = 9;
int bit1 = 7;
int bit2 = 6;
const int trigPin = 10;
const int echoPin = 11;
// const int period = 1000;  // sampling period in ms
// const int steps = 5;     // dimension of grid
bool dataCollected = false;
double duration, distance;
double data[CAR_STEPS][SERVO_SWEEPS];

void setup() {
  pinMode(enable, OUTPUT);
  pinMode(bit1, OUTPUT);
  pinMode(bit2, OUTPUT);

  digitalWrite(bit1, LOW);
  digitalWrite(bit2, LOW);   //Set the motor to off (LOW LOW)
  analogWrite(enable, 255);  //Pull the Enable line to HIGH (basically turns on the motor driver)

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myservo.attach(5);  // attaches the servo on pin 9 to the servo object

  Serial.begin(9600);  // Initialize serial communication for debugging

  // Calculate the step size
  double startValue = cos(STARTING_ANGLE * PI / 180);
  double endValue = cos((180 - STARTING_ANGLE) * PI / 180);

  float step = static_cast<float>(endValue - startValue) / (SERVO_SWEEPS - 1);  //0.0677

  // Populate the array with equally spaced integers
  for (int i = 0; i < SERVO_SWEEPS; i++) {
    angles[i] = startValue + (i * step);
    angles[i] = acos(angles[i]);
    angles[i] = 180 / PI * angles[i];
    angles[i] = 180 - angles[i];
  }
}

void loop() {
  if (dataCollected == true) {
    return;
  }
  for (int i = 0; i < CAR_STEPS; i += 1) {
    for (int pos = angles[SERVO_SWEEPS - 1]; pos >= angles[0]; pos -= 1) {
      myservo.write(pos);
      delay(10);
    }
    delay(500);
    int p = 0;
    for (int pos = angles[0]; pos <= angles[SERVO_SWEEPS - 1]; pos += 1) {
      myservo.write(pos);
      delay(30);

      if (pos == floor(angles[p])) {
        double distance1 = collect();
        // delay(10);
        // double distance2 = collect();
        // delay(10);
        // double distance3 = collect();
        // delay(10);

        // data[i][p] = (distance1 + distance2 + distance3)/3;
        data[i][p] = distance1; 
        Serial.print(data[i][p]);
        Serial.print(", ");
        p++;
      }
      // delay(15);  // waits 30ms for the servo to reach the position
    }
    Serial.println("");

    if (i == CAR_STEPS - 1) continue;

    digitalWrite(bit1, LOW);
    digitalWrite(bit2, HIGH);
    delay(car_distance / CAR_STEPS);  //MOVE THE CAR FOR 100ms
    digitalWrite(bit1, LOW);
    digitalWrite(bit2, LOW);
    delay(500);
  }
  dataCollected = true;
}

float collect() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  distance = (duration * .0343) / 2;
  delayMicroseconds(10);
  return distance;
}
