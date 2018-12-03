//-- void Adafruit_NeoPixel::updateType(t)
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
  auto t = getValue<input_t>(ctx); // neoPixelType
  

  auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel

  object->updateType( t ); // void
  
  emitValue<output_dev>(ctx, object); // for chaining

  emitValue<output_done>(ctx, 1); // pulse
}
