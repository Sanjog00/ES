#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Joystick pins
#define JOYSTICK_X A1
#define JOYSTICK_Y A0

// Buzzer pin
#define BUZZER_PIN 3


LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.backlight();
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // Read the joystick values
  int xValue = analogRead(JOYSTICK_X);
  int yValue = analogRead(JOYSTICK_Y);

  // Map joystick (x/y) direction 
  //only 4 way movement

  int xDirection = (xValue < 400) ? -1 : (xValue > 600) ? 1 : 0;
  int yDirection = (yValue < 400) ? -1 : (yValue > 600) ? 1 : 0;

 
  Serial.print(xDirection);
  Serial.print(",");
  Serial.println(yDirection);

  
  if (Serial.available() > 0) {
    // Read the incoming data
    String data = Serial.readStringUntil('\n');

    if (data.startsWith("SCORE:")) {
      
      String score = data.substring(6);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Score:");
      lcd.setCursor(7, 0);
      lcd.print(score);
    } else if (data == "BUZZER_ON") {
      // Turn on the buzzer
      digitalWrite(BUZZER_PIN, HIGH);
      delay(100); // Buzzer on duration
      digitalWrite(BUZZER_PIN, LOW);
    }
  }

  delay(100);  
}
