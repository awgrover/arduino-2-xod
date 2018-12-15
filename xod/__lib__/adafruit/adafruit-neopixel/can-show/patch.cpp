//-- bool Adafruit_NeoPixel::canShow()
// Our constructor namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
struct State {
  // not used
  };

{{ GENERATED_CODE }}

void evaluate(Context ctx) {

  // only act on trigger, inputs not relevant for this
  if ( !isInputDirty<input_trigger>(ctx) ) return;

  // var names are valid c++ because we got them from the arglist of the c++ method
  

  auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel

  auto rez = object->canShow(  ); // bool
  
  emitValue<output_dev>(ctx, object); // for chaining

  emitValue<output_val>(ctx, rez); // bool
}
