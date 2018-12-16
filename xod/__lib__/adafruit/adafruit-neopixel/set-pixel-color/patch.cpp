//-- void Adafruit_NeoPixel::setPixelColor(n, r, g, b)
// Our constructor namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
struct State {
  // not used
  };

{{ GENERATED_CODE }}

void evaluate(Context ctx) {

  // only act on trigger, inputs not relevant for this
  if ( !isInputDirty<input_trigger>(ctx) ) return;

  // var names are valid c++ because we got them from the arglist of the c++ method
  auto n = getValue<input_n>(ctx); // 
  auto r = getValue<input_r>(ctx); // 
  auto g = getValue<input_g>(ctx); // 
  auto b = getValue<input_b>(ctx); // 
  

  auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel

  object->setPixelColor( n, r, g, b ); // void
  
  emitValue<output_dev>(ctx, object); // for chaining

  
  emitValue<output_done>(ctx, 1); // pulse
}
