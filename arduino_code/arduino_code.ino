#include <math.h>

#define ARRAY_LENGTH(array) (sizeof(array)/sizeof((array)[0]))

#define SUPPLY_VOLTAGE 5.0
#define R_FIXED1_TOP 47000.0
#define R_FIXED2_BTM 1000.0
#define ADC_RESOLUTION_BIT 10.0
#define PIN_OUTER_SENSE A5
#define PIN_INNER_SENSE A0
#define FSR_GRADIENT_LOG -0.3604112
#define MAX_MSG_LEN 14

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_INNER_SENSE, INPUT);
  pinMode(PIN_OUTER_SENSE, INPUT);

  Serial.begin(9600, SERIAL_8N1);
  Serial.setTimeout(0.1);
}

struct fsrdata {
  int inner_sense_analog_val;
  int outer_sense_analog_val;
  float inner_sense_voltage;
  float outer_sense_voltage;
  float inner_sense_resistance;
  float outer_sense_resistance;
  float inner_equiv_force;
  float outer_equiv_force;
};

float convert_ADC_to_V(int adc_reading) {
  // Converts the raw ADC value into equivalent voltage
  return (adc_reading / pow(2, ADC_RESOLUTION_BIT)) * SUPPLY_VOLTAGE;
}

float calc_r_sense(float v_sense) {
  // Calculates the equivalent sense resistor (FSR)
  float r_sense = (R_FIXED2_BTM - (v_sense / SUPPLY_VOLTAGE) * (R_FIXED2_BTM + R_FIXED1_TOP)) / (v_sense / SUPPLY_VOLTAGE - 1);
  return r_sense;
}

float calc_equiv_force(float sense_r) {
  // For a linear relationship in log-log domain in log(y) = m log(x) + log(5),
  // m = (log(5) - log (0.015)) / (log(1) - log(10000000)) for Ohmite FSR07
  // y = 10^(m log10(x) + log10(5))
  float exponent = FSR_GRADIENT_LOG * log10f(sense_r) + 0.6989700;
  return pow(10, exponent);
}

struct fsrdata acquire_data() {
  fsrdata to_return;
  // Start the data acquisition process
  to_return.inner_sense_analog_val = analogRead(PIN_INNER_SENSE);
  to_return.outer_sense_analog_val = analogRead(PIN_OUTER_SENSE);
  to_return.inner_sense_voltage = convert_ADC_to_V(to_return.inner_sense_analog_val);
  to_return.outer_sense_voltage = convert_ADC_to_V(to_return.outer_sense_analog_val);
  to_return.inner_sense_resistance = calc_r_sense(to_return.inner_sense_voltage);
  to_return.outer_sense_resistance = calc_r_sense(to_return.outer_sense_voltage);
  to_return.inner_equiv_force = calc_equiv_force(to_return.inner_sense_resistance);
  to_return.outer_equiv_force = calc_equiv_force(to_return.outer_sense_resistance);
  return to_return;
}

void execute_cmd(String* RxStr) {
  // Store the fsrdata
  static struct fsrdata FSRDATA;
  
  if (*RxStr != "\0") {
    if (*RxStr == "INIT:RXTX:CHK") {
      Serial.flush();
      Serial.println("INIT:RXTX:SUC");
    } else if (*RxStr == "INST:READ:ALL") {
      FSRDATA = acquire_data();
      //Serial.println("DEBUG Entered the RxStr matching");
      Serial.flush();
      String str_to_write = String(FSRDATA.inner_sense_resistance) + "," + String(FSRDATA.outer_sense_resistance) + ","  + String(FSRDATA.inner_sense_voltage) + "," + String(FSRDATA.outer_sense_voltage);
      Serial.println(str_to_write); // println will add a new line character
    } else if (*RxStr == "INST:READ:RES") {
      FSRDATA = acquire_data();
      String str_to_write = String(FSRDATA.inner_sense_resistance) + "," + String(FSRDATA.outer_sense_resistance);
      Serial.println(str_to_write);
    } else if (*RxStr == "INST:READ:VOL") {
      FSRDATA = acquire_data();
      String str_to_write = String(FSRDATA.inner_sense_voltage) + "," + String(FSRDATA.outer_sense_voltage);
      Serial.println(str_to_write);
    } else {
      Serial.println("ERROR Command not recognised: Command Invalid");
    }
  }
}

void loop() { 
  // Start Rx, Tx process
  static String RxStr = "";

  while (Serial.available() > 0) {
    static char message[MAX_MSG_LEN];
    static unsigned int message_pos = 0;
    char inputByte = Serial.read();

    if (inputByte != "\n" && (message_pos < MAX_MSG_LEN -1)) {
      message[message_pos] = inputByte;
      message_pos++;
    } else if (inputByte == "\n" && (message_pos < MAX_MSG_LEN -1)) {
      message_pos = 0;
    } else {
      RxStr = String(message);
      //Serial.println("DEBUG Command Received: " + RxStr);
      execute_cmd(&RxStr);
      message_pos = 0;
      RxStr = ""; // Clear the RxStr string
    }
  }
}
