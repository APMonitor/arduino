/*
  Temperature Control Lab Firmware

  This firmware is initially loaded into the Temperature Control Laboratory Arduino. 
  The firmware scans the serial port looking for case-insensitive commands:

  Q1 int    set Heater 1, range 0 to 255 subject to limit
  Q2 int    set Heater 2, range 0 to 255 subject to limit
  T1        get Temperature T1, returns deg C as string
  T2        get Temperature T2, returns dec C as string
  VERSION   get firmware version string
  X         shutdown, reset required

  LED1 on dim during normal operation.
  LED1 on bright when if either is on
  LED1 blinks if high temperature alarm is on

  Receipt of any unrecognized commands cause the board to shutdown and Reset is required.
*/

// constants
const String vers = "0.02";    // version of this firmware
const int baud = 9600;         // serial baud rate
const char sp = ' ';           // command separator
const char nl = '\n';          // command terminator
const int timeout = 300;       // device timeout in seconds

// pin numbers corresponding to signals on the TC Lab Shield
const int pinT1   = 0;         // T1
const int pinT2   = 2;         // T2
const int pinQ1   = 3;         // Q1
const int pinQ2   = 5;         // Q2
const int pinLED1 = 9;         // LED1

// high limits expressed (units of pin values)
const int limQ1   = 150;       // Q1 limit
const int limQ2   = 150;       // Q2 limit
const int limT1   = 310;       // T1 high alarm (50 deg C)
const int limT2   = 310;       // T2 high alarm (50 deg C)

// LED1 levels
const int hiLED   =  50;       // high limit of LED
const int loLED   = hiLED/16;  // low LED

// global variables
char Buffer[64];               // buffer for parsing serial input
String cmd;                    // command 
int pv;                        // command pin value
int ledStatus;                 // 0:off, 1:dim, 2:bright 3:dim blink 4:bright blink
int brdStatus = 1;             // board status 0:reset required 1:ok
int Q1 = 0;                    // last value written to Q1 pin
int Q2 = 0;                    // last value written to Q2 poin
int alarmStatus = 0;           // hi temperature alarm status
int tprev;                     // millis for last command

// set Heaters to value. Hard limits imposed.
void setHeater1(int pv) {
  if (brdStatus > 0) {
    Q1 = max(0, min(limQ1, pv));
    analogWrite(pinQ1, Q1);
  }
}

void setHeater2(int pv) {
  if (brdStatus > 0) {
    Q2 = max(0, min(limQ2, pv));
    analogWrite(pinQ2, Q2);
  }
}

// parse serial input
void SerialParse(void) {
  // read serial input
  int ByteCount = Serial.readBytesUntil(nl,Buffer,sizeof(Buffer));
  String read_ = String(Buffer);
  memset(Buffer,0,sizeof(Buffer));
   
  // separate command from associated data
  int idx = read_.indexOf(sp);
  cmd = read_.substring(0,idx);
  cmd.trim();
  cmd.toUpperCase();

  // extract data. toInt() returns 0 on error
  String data = read_.substring(idx+1);
  data.trim();
  pv = data.toInt();

  // issue shutdown if no command received in within timeout seconds
  if (ByteCount > 0) {
    tprev = millis();
  } else {
    if ((millis() - tprev) > 1000*timeout) {
      cmd = "X";
    }
  }
}

// dispatch commands
void CommandDispatch(void) {
  // process commands
  if (cmd == "Q1") {
    setHeater1(pv);
    Serial.println(Q1);
  }
  else if (cmd == "Q2") {
    setHeater2(pv);
    Serial.println(Q2);
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
    Serial.println("TClab Firmware Version " + vers);
  }
  // shutdown
  else if ((cmd == "X") or (cmd.length() > 0)) {
    Serial.println("TClab in Sleep Mode. Please reset.");
    setHeater1(0);
    setHeater2(0);
    brdStatus = 0;
  }
}

// check alarms and update status on LED1
void AlarmCheck(void) {
  if (analogRead(pinT1) > limT1) {
    alarmStatus = 1;
  }
  else if (analogRead(pinT2) > limT2) {
    alarmStatus = 1;
  }
  else {
    alarmStatus = 0;
  }
}

// update LED
void LEDUpdate(void) {
  // determine led status
  ledStatus = brdStatus;
  if ((Q1 > 0) or (Q2 > 0)) {
    ledStatus = 2;
  }
  if (alarmStatus > 0) {
    ledStatus = 3;
    if ((Q1 > 0) or (Q2 > 0)) {
      ledStatus = 4;
    }
  }
  // update led depending on ledStatus
  if (ledStatus == 0) {               // board is off, no alarms, reset required
    analogWrite(pinLED1, 0);
  }
  else if (ledStatus == 1) {          // normal operation with heaters off
    analogWrite(pinLED1, loLED);
  }
  else if (ledStatus == 2) {          // normal operation with one or both heaters on
    analogWrite(pinLED1, hiLED);
  }
  else if (ledStatus == 3) {          // high temperature alarm with heater off
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, loLED);
    } else {
      analogWrite(pinLED1, 0);
    }
  }
  else if (ledStatus == 4) {          // hight temperature alarm with either heater on
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, hiLED);
    } else {
      analogWrite(pinLED1, 0);
    }
  }
}

// arduino setup procedure
void setup() {
  analogReference(EXTERNAL);
  Serial.begin(baud); 
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  setHeater1(0);
  setHeater2(0);
}

// arduino main event loop
void loop() {
  SerialParse();
  CommandDispatch();
  AlarmCheck();
  LEDUpdate();
}
