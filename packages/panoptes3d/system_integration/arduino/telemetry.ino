
const int maxChars = 10;
char command[maxChars]
bool haveNewCmd = false;

void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);


    serial.println("|r|");
}

void loop(){
    if (haveNewCmd == false){
        readSerial();
    }
    else if (haveNewCmd == true){
        execute_command();
        haveNewCmd = false;
    }
}

void readSerial(){
    char currentChar;
    bool recievingCmd = false;
    int i = 0;

    while (Serial.available() > 0){
    currentChar = Serial.read();
    if (currentChar == byte('<') && recievingCmd == false){
      recievingCmd = true;
    }
    else if (currentChar != byte('>') && recievingCmd == true && i < maxChars){
      command[i] = currentChar;
      i++;
    }
    else {
      command[i] = '\0';
      i = 0;
      recievingCmd = false;
      haveNewCmd = true;
      break;
    }
  }
}

void execute_command(){
  char baseCmd[maxChars] = {0};
  char * strIdx;
  strIdx = strtok(command,",");
  strcpy(baseCmd, strIdx);
  int switchCmd = atoi(baseCmd);
  strIdx = strtok(NULL, ",");

  // switch for command execution
  // use for setting on/off reading of telemetry in void loop()

}