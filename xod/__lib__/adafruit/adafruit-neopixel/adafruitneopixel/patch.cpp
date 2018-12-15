//-- constructor Adafruit_NeoPixel(n, p, t)
#pragma XOD require "https://github.com/adafruit/Adafruit_NeoPixel"

// Include C++ library:
{{#global}}
#include <Adafruit_NeoPixel.h>
{{/global}}

// Our namespace should be: adafruit__adafruit_neopixel__adafruitneopixel
// Reserve the space for the object.
struct State {
  uint8_t mem[sizeof(Adafruit_NeoPixel)];
  };
using Type = Adafruit_NeoPixel*; // 'Type' is assumed by xod code-generator

{{ GENERATED_CODE }}

void evaluate(Context ctx) {
  // It should be evaluated only once on the first (setup) transaction
  if (!isSettingUp()) return; // FIXME: relax this?

  auto state = getState(ctx);

  // var names are valid c++ because we got them from the arglist of the c++ constructor
  auto n = getValue<input_n>(ctx); // int
  auto p = getValue<input_p>(ctx); // int
  auto t = getValue<input_t>(ctx); // neoPixelType
  

  Type object = new (state->mem) Adafruit_NeoPixel( n, p, t );

  emitValue<output_adafruitneopixel>(ctx, object);
  emitValue<output_done>(ctx, object);
}
