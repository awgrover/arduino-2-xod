//-- void Adafruit_NeoPixel::setPin(p)
// Our constructor namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
struct State {
  // not used
  };

{{ GENERATED_CODE }}

void evaluate(Context ctx) {

  if (
    !isInputDirty<input_adafruitneopixel>(ctx)
  ) return;

  // var names are valid c++ because we got them from the arglist of the c++ method
  auto p = getValue<input_p>(ctx); // int
  

  auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel

  object->setPin( p ); // void
  
  emitValue<output_dev>(ctx, object); // for chaining

  emitValue<output_done>(ctx, 1); // pulse
}
