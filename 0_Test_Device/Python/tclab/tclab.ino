/*
  TCLab Temperature Control Lab Firmware
  Jeffrey Kantor, Initial Version
  John Hedengren, Modified
  Oct 2017

  This firmware is loaded into the Temperature Control Laboratory Arduino to
  provide a high level interface to the Temperature Control Lab. The firmware
  scans the serial port looking for case-insensitive commands:

  Q1        set Heater 1, range 0 to 100% subject to limit (0-255 int)
  Q2        set Heater 2, range 0 to 100% subject to limit (0-255 int)
  T1        get Temperature T1, returns deg C as string
  T2        get Temperature T2, returns dec C as string
  VER       get firmware version string
  X         stop, enter sleep mode

  Limits on the heater can be configured with the constants below.
*/

// constants
const String vers = "1.01";    // version of this firmware
const int baud = 9600;         // serial baud rate
const char sp = ' ';           // command separator
const char nl = '\n';          // command terminator

// pin numbers corresponding to signals on the TC Lab Shield
const int pinT1   = 0;         // T1
const int pinT2   = 2;         // T2
const int pinQ1   = 3;         // Q1
const int pinQ2   = 5;         // Q2
const int pinLED  = 9;         // LED

// global variables
char Buffer[64];               // buffer for parsing serial input
String cmd;                    // command 
float pv;                      // pin value
float level;                   // LED level (0-100%)
float Q1 = 0;                  // value written to Q1 pin
float Q2 = 0;                  // value written to Q2 pin
int iwrite = 0;                // integer value for writing
float dwrite = 0;              // float value for writing
int n = 10;                    // number of samples for each temperature measurement

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
  pv = data.toFloat();
}

// sum of output = 300
// Q1_max = 200
// Q2_max = 100
void dispatchCommand(void) {
  if (cmd == "Q1") {
    Q1 = max(0.0, min(100.0, pv));
    iwrite = int(Q1 * 2.0); // 2.55 max
    iwrite = max(0, min(255, iwrite));    
    analogWrite(pinQ1, iwrite);
    Serial.println(Q1);
  }
  else if (cmd == "Q2") {
    Q2 = max(0.0, min(100.0, pv));
    iwrite = int(Q2 * 1.0); // 2.55 max
    iwrite = max(0, min(255, iwrite));
    analogWrite(pinQ2, iwrite);
    Serial.println(Q2);
  }
  else if (cmd == "T1") {
    float mV = 0.0;
    float degC = 0.0;
    for (int i = 0; i < n; i++) {
      mV = (float) analogRead(pinT1) * (3300.0/1024.0);
      degC = degC + (mV - 500.0)/10.0;
    }
    degC = degC / float(n);   
    Serial.println(degC);
  }
  else if (cmd == "T2") {
    float mV = 0.0;
    float degC = 0.0;
    for (int i = 0; i < n; i++) {
      mV = (float) analogRead(pinT2) * (3300.0/1024.0);
      degC = degC + (mV - 500.0)/10.0;
    }
    degC = degC / float(n);
    Serial.println(degC);
  }
  else if ((cmd == "V") or (cmd == "VER")) {
    Serial.println("TCLab Firmware Version " + vers);
  }
  else if (cmd == "LED") {
    level = max(0.0, min(100.0, pv));
    iwrite = int(level * 0.5);
    iwrite = max(0, min(50, iwrite));    
    analogWrite(pinLED, iwrite);
    Serial.println(level);
  }  
  else if (cmd == "X") {
    analogWrite(pinQ1, 0);
    analogWrite(pinQ2, 0);
    Serial.println("Stop");
  }
}

// check temperature and shut-off heaters if above high limit
void checkTemp(void) {
    float mV = (float) analogRead(pinT1) * (3300.0/1024.0);
    float degC = (mV - 500.0)/10.0;
    if (degC >= 100.0) {
      Q1 = 0.0;
      Q2 = 0.0;
      analogWrite(pinQ1, 0);
      analogWrite(pinQ2, 0);
      Serial.println("High Temp 1 (>100C): ");
      Serial.println(degC);
    }
    mV = (float) analogRead(pinT2) * (3300.0/1024.0);
    degC = (mV - 500.0)/10.0;
    if (degC >= 100.0) {
      Q1 = 0.0;
      Q2 = 0.0;
      analogWrite(pinQ1, 0);
      analogWrite(pinQ2, 0);
      Serial.println("High Temp 2 (>100C): ");
      Serial.println(degC);
    }
}

// arduino startup
void setup() {
  analogReference(EXTERNAL);
  Serial.begin(baud); 
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  analogWrite(pinQ1, 0);
  analogWrite(pinQ2, 0);
}

// arduino main event loop
void loop() {
  parseSerial();
  dispatchCommand();
  checkTemp();
}
