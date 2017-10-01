
/*
  Temperature Control Lab ArduinoFirmware Version 0.1

  This firmware is initially loaded into the Temperature Lab Arduino devices. The firmware monitors
  the serial port looking for commands in the form

  T1        : read pin for temperature T1, return string in deg C
  T2        : read pin temperature T2, return string in deg C
  Q1 data   : write pin for Heater 1, integer data in range 0 to 255
  Q2 data   : write pin for Heater 2, integer data in range 0 to 255
  LED1 data : write pin for LED1, integer data in range 0 to 255, rescaled to 0 to 51
  version   : read firmware version
*/

String vers = "0.1";         // version of this firmware
int baud = 9600;             // serial baud rate
int ByteCount;               // for parsing serial input
char Buffer[64];             // buffer for parsing serial input
char sp = ' ';               // command separator
char nl = '\n';              // command terminator

int pinT1 = 0;               // pin number to read T1      returns deg C as string
int pinT2 = 2;               // pin number to read T2      returns deg C as string
int pinQ1 = 3;               // pin number to write Q1     accepts range 0 to 255
int pinQ2 = 5;               // pin number to write Q2     accepts range 0 to 255
int pinLED1 = 9;             // pin number to write LED1   accepts range 0 to 255 rescales to 0 51

/* converts string to integer */
int Str2int (String Str_value)
{
  char buffer[10]; //max length is three units
  Str_value.toCharArray(buffer, 10);
  int int_value = atoi(buffer);
  return int_value;
}

/* parses serial input for commands */
void SerialParser(void) {
  ByteCount = Serial.readBytesUntil(nl,Buffer,sizeof(Buffer));
  String read_ = String(Buffer);
  int idx = read_.indexOf(sp);
  // separate command from associated data
  String cmd = read_.substring(0,idx);
  String data = read_.substring(idx+1);
  memset(Buffer,0,sizeof(Buffer));
  
  // determine command sent
  if (cmd == "version") {
    Serial.println("TC Laboratory ArduinoFirmware Version " + vers);
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
  else if (cmd == "LED1") {
    int pv = Str2int(data);
    pv = max(0,min(255,pv)); 
    analogWrite(pinLED1,int(pv/5));
  }
  else if (cmd == "Q1") {
    int pv = Str2int(data);
    pv = max(0,min(255,int(pv)));
    analogWrite(pinQ1,pv);
  }
  else if (cmd == "Q2") {
    int pv = Str2int(data);
    pv = max(0,min(255,int(pv)));
    analogWrite(pinQ2,pv);
  }
}

void setup()  {
  analogReference(EXTERNAL);
  Serial.begin(baud); 
    while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  Serial.flush();
}

void loop() {
   SerialParser();
}
