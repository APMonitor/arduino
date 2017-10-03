/*
  TCLab Temperature Control Lab Firmware
  Jeffrey Kantor
  October, 2017

  This firmware is loaded into the Temperature Control Laboratory Arduino to
  provide a high level interface to the Temperature Control Lab. The firmware
  scans the serial port looking for case-insensitive commands:

  A         software restart
  Q1 int    set Heater 1, range 0 to 255 subject to limit
  Q2 int    set Heater 2, range 0 to 255 subject to limit
  T1        get Temperature T1, returns deg C as string
  T2        get Temperature T2, returns dec C as string
  V         get firmware version string
  X         stop, enter sleep mode

  Limits on the heater can be configured with the constants below.

  Status is indicated by LED1 on the Temperature Control Lab. The status
  conditions are:

      LED1        LED1
      Brightness  State
      ----------  -----
      dim         steady     Normal operation, heaters off
      bright      steady     Normal operation, heaters on
      dim         blinking   High temperature alarm on, heaters off
      bright      blinking   High temperature alarm on, heaters on
      dim         slow blink Sleep mode, needs hardware or software reset

  The Temperature Control Lab enters sleep mode if it receives no host commands
  during a timeout period (configure below), receives an "X" command, or receives
  an unrecognized command from the host. Heaters are shutdown in sleep mode, 
  though temperature can continue to be monitored, and high temperature alarm is
  still active on LED1.

  Sleep mode is exited upon either a hardware reset with the button on the Arduino
  board, or software reset with the "A" command.

  The constants can be used to configure the firmware.
*/

// constants
const String vers = "0.03";    // version of this firmware
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
const int hiLED   =  50;       // hi LED
const int loLED   = hiLED/16;  // lo LED

// global variables
char Buffer[64];               // buffer for parsing serial input
String cmd;                    // command 
int pv;                        // command pin value
int ledStatus;                 // 0: sleep mode
                               // 1: loLED
                               // 2: hiLED
                               // 3: loLED blink
                               // 4: hiLED blink
int brdStatus = 1;             // board status 0:sleep, 1:normal
int Q1 = 0;                    // last value written to Q1 pin
int Q2 = 0;                    // last value written to Q2 poin
int alarmStatus;               // hi temperature alarm status
int tlast;                     // millis when last host command

// set Heater 1 to pv with hard limits imposed.
void setHeater1(int pv) {
  if (brdStatus > 0) {
    Q1 = max(0, min(limQ1, pv));
    analogWrite(pinQ1, Q1);
  }
}

// set Heater 2 to pv with hard limits imposed.
void setHeater2(int pv) {
  if (brdStatus > 0) {
    Q2 = max(0, min(limQ2, pv));
    analogWrite(pinQ2, Q2);
  }
}

void parseSerial(void) {
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
}

void checkTimeout(void) {
  if (cmd.length() > 0) {
    tlast = millis();
  } else {
    if ((long) (millis() - tlast) > (long) 1000*timeout) {
      setHeater1(0);
      setHeater2(0);
      brdStatus = 0;
    }
  }
}

void dispatchCommand(void) {
  if (cmd == "A") {
    brdStatus = 1;
    setHeater1(0);
    setHeater2(0);
    Serial.println("Start");
  }
  else if (cmd == "Q1") {
    setHeater1(pv);
    Serial.println(Q1);
  }
  else if (cmd == "Q2") {
    setHeater2(pv);
    Serial.println(Q2);
  }
  else if (cmd == "T1") {
    float mV = (float) analogRead(pinT1) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "T2") {
    float mV = (float) analogRead(pinT2) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    Serial.println(degC);
  }
  else if (cmd == "V") {
    Serial.println("TClab Firmware Version " + vers);
  }
  else if ((cmd == "X") or (cmd.length() > 0)) {
    setHeater1(0);
    setHeater2(0);
    brdStatus = 0;
    Serial.println("Stop");
  }
}

void checkAlarm(void) {
  if ((analogRead(pinT1) > limT1) or (analogRead(pinT2) > limT2)) {
    alarmStatus = 1;
  }
  else {
    alarmStatus = 0;
  }
}

void updateStatus(void) {
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
  if (ledStatus == 0) {               // board is in sleep mode
    if ((millis() % 5000) > 1000) {
      analogWrite(pinLED1, 0);
    } else {
      analogWrite(pinLED1, loLED);
    }
  }
  else if (ledStatus == 1) {          // normal operation, heaters off
    analogWrite(pinLED1, loLED);
  }
  else if (ledStatus == 2) {          // normal operation, a heater on
    analogWrite(pinLED1, hiLED);
  }
  else if (ledStatus == 3) {          // high temperature alarm, heater off
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, loLED);
    } else {
      analogWrite(pinLED1, 0);
    }
  }
  else if (ledStatus == 4) {          // hight temperature alarm, a heater on
    if ((millis() % 2000) > 1000) {
      analogWrite(pinLED1, hiLED);
    } else {
      analogWrite(pinLED1, 0);
    }
  }
}

// arduino startup
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
  parseSerial();
  checkTimeout();
  dispatchCommand();
  checkAlarm();
  updateStatus();
}
