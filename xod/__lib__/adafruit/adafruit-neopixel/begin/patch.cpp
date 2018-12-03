//-- void Adafruit_NeoPixel::begin()
// Our constructor namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
struct State {
  // not used
  };

{{ GENERATED_CODE }}

void evaluate(Context ctx) {

  // no inputs

  // var names are valid c++ because we got them from the arglist of the c++ method
  

  auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel

  //Serial.print(millis());Serial.print(F(" "));Serial.print(F("begin: "));Serial.println((int)object);
  object->begin(  ); // void
  
  emitValue<output_dev>(ctx, object); // for chaining

  emitValue<output_done>(ctx, 1); // pulse
}
