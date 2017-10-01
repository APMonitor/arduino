/*
  Temperature Control Lab Firmware

  This firmware is initially loaded into the Temperature Control Laboratory Arduino. 
  The firmware scans the serial port looking for case-insensitive commands:

  LED1 int  set LED1, range 0 to 255, limit to 50
  Q int     set Heater 1, range 0 to 255,  limit to 150 to prevent overheating
            (note: Q turns off Heater 2 as safety precaution)
  Q1 int    set Heater 1, range 0 to 255,  limit to 150 to prevent overheating
  Q2 int    set Heater 2, range 0 to 255,  limit to 150 to prevent overheating
  T         get Temperature T1, returns deg C as sring
  T1        get Temperature T1, returns deg C as string
  T2        get Temperature T2, returns dec C as string
  VERSION   get firmware version string
  X         shutdown, set LED1, Q1, Q2 to zero

  LED1 is on during normal operation.

  LED1 is on bright for high temperature alarm.

  Receipt of any unrecognized commands cause the board to shutdown and report
  status by blinking LED1. Reset is required.
*/

// global variables
char Buffer[64];         // buffer for parsing serial input

// constants
const String vers = "0.1";     // version of this firmware
const int baud = 19200;        // serial baud rate
const char sp = ' ';           // command separator
const char nl = '\n';          // command terminator

// pin numbers corresponding to signals on the TC Lab Shield
const int pinT1   = 0;         // T1
const int pinT2   = 2;         // T2
const int pinQ1   = 3;         // Q1
const int pinQ2   = 5;         // Q2
const int pinLED1 = 9;         // LED1

// high limits expressed (units of pin values)
const int limLED1 =  50;       // LED1 limit
const int limQ1   = 150;       // Q1 limit
const int limQ2   = 150;       // Q2 limit
const int limT1   = 310;       // T1 high alarm (approx. 50 deg C)
const int limT2   = 310;       // T2 high alarm (approx. 50 deg C)

// parse and process serial input
void SerialParser(void) {
  // read serial input
  int ByteCount = Serial.readBytesUntil(nl,Buffer,sizeof(Buffer));
  String read_ = String(Buffer);
  memset(Buffer,0,sizeof(Buffer));
  
  // separate command from associated data
  int idx = read_.indexOf(sp);
  String cmd = read_.substring(0,idx);
  cmd.trim();
  cmd.toUpperCase();

  // extract data. toInt() returns 0 on error
  String data = read_.substring(idx+1);
  data.trim();
  int pv = data.toInt();
  
  // process commands
  if (cmd == "LED1") {
    analogWrite(pinLED1, max(0,min(limLED1,pv)));
  }
  else if (cmd == "Q") {
    analogWrite(pinQ1, max(0,min(limQ1,pv)));
    analogWrite(pinQ2, 0);
  }
  else if (cmd == "Q1") {
    analogWrite(pinQ1, max(0,min(limQ1,pv)));
  }
  else if (cmd == "Q2") {
    analogWrite(pinQ2, max(0,min(limQ2,pv)));
  }
  else if (cmd == "T") {
    float mV = (float)analogRead(pinT1) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "T1") {
    float mV = (float)analogRead(pinT1) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "T2") {
    float mV = (float)analogRead(pinT2) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "VERSION") {
    Serial.println("TC Laboratory Firmware Version " + vers);
  }
  // shutdown
  else if (cmd == "X") {
    analogWrite(pinLED1, 0);
    analogWrite(pinQ1, 0);
    analogWrite(pinQ2, 0);
  }
  // shut down on unrecognized command
  else if (cmd.length() > 0) {
    Serial.println("Unrecognized command. Please reset.");
    analogWrite(pinQ1, 0);
    analogWrite(pinQ2, 0);
    while (true) {
      analogWrite(pinLED1, limLED1);
      delay(250);
      analogWrite(pinLED1, 0);
      delay(250);
    }
  }
}

void CheckAlarms(void) {
  if ((analogRead(pinT1) > limT1) or (analogRead(pinT2) > limT2)) {
    analogWrite(pinLED1,limLED1);
  } else {
    analogWrite(pinLED1,limLED1/16);
  }
}

void setup() {
  analogReference(EXTERNAL);
  Serial.begin(baud); 
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  Serial.flush();
  analogWrite(pinQ1,0);
  analogWrite(pinQ2,0);
}

void loop() {
  SerialParser();
  CheckAlarms();
}
