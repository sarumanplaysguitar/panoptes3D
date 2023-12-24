////////////////////////////////////////////////////////////////////////////////////////////////
// Sends telemetry data over serial in either:                                                //
// Stream                                                                                     //
//     - Send serial <1> to start stream, <2> to end stream                                   //
// Request/Post                                                                               //
//     - Send <3> to recieve a single point of telemetry at the current time                  //
// Data format: |[Roll in degrees, pitch in degrees, yaw in degrees, azimuth in degrees]      //
////////////////////////////////////////////////////////////////////////////////////////////////

#include <Adafruit_LSM303_Accel.h>
#include <Adafruit_LIS2MDL.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

// Sensors
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(12312);
Adafruit_LIS2MDL mag = Adafruit_LIS2MDL(23123);

const int maxChars = 10;
char command[maxChars];
bool haveNewCmd = false;

bool sendTelemetry = false;

void setup(){
    delay(1000);
    Serial.begin(9600);

    if (!accel.begin()){
      Serial.println("Wiring problem with accelerometer");
      while(1);
    }

    accel.setRange(LSM303_RANGE_4G);
    accel.setMode(LSM303_MODE_NORMAL);

    if (!mag.begin()){
      Serial.println("No magnetometer found, wiring problem?");
      while(1);
    }

    Serial.println("|r|");
}

void loop(){

    if (haveNewCmd == false){
        readSerial();
    }
    
    if (haveNewCmd == true){
        execute_command();
        haveNewCmd = false;
    }

    if (sendTelemetry == true){
      getTelemetry();
    }

    delay(100);
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

  if (switchCmd == 1){
    sendTelemetry = true;
  }
  
  if (switchCmd == 2) {
    sendTelemetry = false;
  }

  if (switchCmd == 3) {
    getTelemetry();
  }

}

void getTelemetry(){
  sensors_event_t event;
  sensors_event_t mag_event;
  accel.getEvent(&event);
  mag.getEvent(&mag_event);

  float a_X = event.acceleration.x;
  float a_Y = event.acceleration.y;
  float a_Z = event.acceleration.z;

  // Calibration for this specific sensor, values found using MotionCal.exe
  float m_X = 0.963 * (mag_event.magnetic.x + 24.77) + 0.004 * (mag_event.magnetic.y + 40.23) -0.022 * (mag_event.magnetic.z + 28.43);
  float m_Y = 0.004 * (mag_event.magnetic.x + 24.77) + 1.042 * (mag_event.magnetic.y + 40.23) - 0.005 * (mag_event.magnetic.z + 28.43);
  float m_Z = -0.022 * (mag_event.magnetic.x + 24.77) - 0.005 * (mag_event.magnetic.y + 40.23) + 0.998 * (mag_event.magnetic.z + 28.43);

  float azimuth = (atan2(m_Y, m_X) * 180) / -3.14159;

  if (azimuth < 0){
    azimuth = 360 + azimuth;
  }

  float roll = (atan2(event.acceleration.y, event.acceleration.z) * 180) / -3.14159;
  float pitch = (atan2(-1 * event.acceleration.x, sqrt(event.acceleration.y * event.acceleration.y + event.acceleration.z * event.acceleration.z)) * 180) / -3.14159;

  float horizontal_mag_vector_x = m_X * cos(pitch * (3.14159 / 180)) + m_Z * sin(pitch * (3.14159 / 180));
  float horizontal_mag_vector_y = m_X * sin(roll * (3.14159 / 180)) * sin(pitch * (3.14159 / 180)) + m_Y * cos(roll * (3.14159 / 180)) - m_Z * sin(roll * (3.14159 / 180)) * cos(pitch * (3.14159 / 180));

  float yaw = 180 / 3.14159 * atan2(horizontal_mag_vector_y, horizontal_mag_vector_x);


  /* Credit for azimuth_tilt_compensation: 
  Michael J. Caruso
  Honeywell, SSEC
  http://www.brokking.net/YMFC-32/YMFC-32_document_1.pdf
  */
  float Xh = m_X * cos(pitch * (3.14159 / 180)) + m_Y * sin(roll * 3.14159/180) * sin(pitch * (3.14159 / 180)) - m_Z * cos(roll * 3.14159/180) * sin(pitch * (3.14159 / 180));
  float Yh = m_Y * cos(roll * 3.14159/180) + m_Z * sin(roll * 3.14159/180);

  float azimuth_tilt_compensated;
  if (Xh < 0){
    azimuth_tilt_compensated = 180 - atan(Yh/Xh) * 180/3.14159;
  }
  else if ((Xh > 0) && (Yh < 0)){
    azimuth_tilt_compensated = -1 * atan(Yh/Xh) * 180/3.14159;
  }
  else if ((Xh > 0) && (Yh > 0)){
    azimuth_tilt_compensated = 360 - atan(Yh/Xh) * 180/3.14159;
  }
  else if ((Xh == 0) && (Yh < 0)){
    azimuth_tilt_compensated = 90;
  }
  else if ((Xh == 0) && (Yh > 0)){
    azimuth_tilt_compensated = 270;
  }

  Serial.print("|[");
  Serial.print(roll); Serial.print(",");
  Serial.print(pitch); Serial.print(",");
  Serial.print(yaw); Serial.print(",");
  Serial.print(azimuth_tilt_compensated);
  Serial.println("]|");

}
