//-- int * Adafruit_NeoPixel::pixels getter/setter
// Our constructor namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
struct State {
  // not used
  };

{{ GENERATED_CODE }}

void evaluate(Context ctx) {

  // Seems like an ugly pattern...

  // Set the value if incoming value is dirty (and emit it)
  if ( isInputDirty<input_val> ) {
    auto value  = getValue<input_val>(ctx); // int *
    auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel
    object->pixels = value;

    emitValue<output_dev>(ctx, object);
    emitValue<output_out>(ctx, value);
  }

  // Emit the value if object is dirty ? or by pulse?
  else if ( isInputDirty<input_adafruitneopixel> ) {
    auto object  = getValue<input_adafruitneopixel>(ctx); // Adafruit_NeoPixel
    auto value = object->pixels;

    emitValue<output_dev>(ctx, object);
    emitValue<output_out>(ctx, value );
    }

  else {
    // not dirty, do nothing
    }

}
