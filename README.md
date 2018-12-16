# Automatic XOD Library from Arduino Library

# Summary and Usage

Up till now ([XOD](https://xod.id) v0.25.2 2018-11-06), it has required a degree of expertise to make [Arduino IDE libraries](https://www.arduino.cc/en/Guide/Libraries) [usable in XOD](https://xod.io/docs/guide/wrapping-arduino-libraries). This is quite a barrier to using XOD for many projects. For example, XOD does not have the NeoPixel library (@bradzilla84 has a [partial one](https://xod.io/libs/bradzilla84/neopixel/)!), and Neopixels are very popular.

I thought it would be possible to automatically generate a XOD library from an Arduino library. The class in the Arduino library becomes the "object" in XOD via the constructor, and each method becomes a node. 

I assumed that the result might be a bit crude, and low-level. But, it provides all the features, and a XODer could then make a prettier library around it. If it only gets 80% right, that's probably good enough to use for many things (and can be manually repaired later). So, automatic conversion could make libraries available faster, and more accessible.

Also, if the XOD library were parallel to the Arduino library, then existing tutorials for the Arduino IDE world would give some idea of how to use them in XOD.

My vision is to see this installed in XOD itself, or in the XOD website. We could build up the libraries quite quickly. As they are auto-converted, we should request refinement/repair/wrapping on the XOD forum!

I chose Adafruit's [NeoPixel V1.1.7](https://github.com/adafruit/Adafruit_NeoPixel) library to try. The generated library is at [in my xod libs on github](https://github.com/awgrover/xod_lib/tree/master/lib/awgrover/adafruit-neopixel-ll), and published in the usual [xod-libs](https://xod.io/libs/awgrover/adafruit-neopixel-ll/).

# Playing With The Auto-converted Neopixel Library

It is [published](https://xod.io/libs/awgrover/adafruit-neopixel-ll/), so the usual `Add Library...` should work.

This is a prototype, low-level, mechanical conversion. It may not be completely in the spirit of XOD. There are some discussions on the [XOD Forum](https://forum.xod.io/) about many aspects bearing on this conversion.

This conversion is known to have some broken bits: several methods were skipped, arguments in some methods were skipped, etc. 

You should be able to refer to existing tutorials, code, etc., and use this library in a parallel fashion. Each method has become a patch, so you'll see the same words and patterns of use (I had to change the spelling slightly: all lower-case, and some dashes).

The library has the philosophy that the patches are "impure" and cause side-effects (i.e. they change the state of the object, and the real world). It seems that the right way to handle those kinds of things is to provide a "trigger" input pulse on the patches. A patch will not respond to it's other inputs _until_ a pulse is seen. And, then it will _always_ "do it's thing." The patch will emit a pulse, which is very convenient for chaining to the next patch to keep things in the right time-order.

There's a problem with this pattern: if you want to "do something" (like `set-pixel-color`) based on each count of a counter, then you somehow have to go from "data" to "pulse". The only mechanism I know of is `awgrover/conversions/data-to-pulse`.

You can see the pulse chaining in my examples.

* Install the library (`awgrover/adafruit-neopixel-ll`) as you would any other published XOD library.
  * But, you also need my other library [awgrover/conversions](https://xod.io/libs/awgrover/conversions/) (via the usual `Add Library...`).
* Examples
  * See the "example-*" patches in the library.
  * `example-simple` is very similar to the Arduino IDE library example `simple`.
  * `example-rgb-revelation` helps you figure out the RGB/GRB/BGR/etc order of your colors.
  * `example-rgb-revelation1pixel` does the same thing, but only requires 1 NeoPixel.
* Basic library usage. Very much like the Arduino IDE.
  * "make" the neopixel object
      * Use the `adafruitneopixel` patch to represent a single neopixel "string". Which is "all the neopixels on the same Arduino pin". Because you can chain neopixel devices together.
      * `n` is the number of "pixels" in the string.
      * `p` is the pin the string is on. Just like for the Arduino IDE, most digital pins work.
      * `t` is the RGB order. My neopixel happens to be GRB. Sadly, you have figure this out and use the right value. See "Example: Figure out RGB order" below! You can start with '6' to get going, but your colors may be wrong.
  * Put the `begin` patch in, and link both the `adafruitneopixel` and `done` (pulse).
  * Now add various patches like `set-pixel-color`, chaining together via the `done`/`trigger` outputs.
      * You can use a `bus` for the `adafruitneopixel` object.
      * The object is needed as input for each patch (`adafruitneopixel`), and is emitted as `dev`.
      * Don't forget `show`! Just like in the Arduino IDE.
      * The "methods" from Arduino IDE are patches in XOD.

## Properties

As a demonstration, I had converted instance-variables to nodes. This is to be discussed! You don't actually want to use them, because they are all actually private in this library, and won't work. Also, it slows the XOD IDE down quite a bit.

## Examples

I'm working on more examples, copying the Arduino [library's examples](https://github.com/adafruit/Adafruit_NeoPixel/tree/master/examples). That will be a good further test of what I've done. I'll update my github xod library as I go and add to this thread. Look for examples, as patches, in the library named like `example-*`.

### Example: "revelation" -- Figure out RGB order

These 2 examples are in the XOD library, but not the Adafruit Arduino /inlibrary, and seem very useful to me.

Apparently, neopixels come in many flavors: they aren't all in the obvious RGB order. `set-pixel-color' takes a red, green, and blue argument, but if you haven't set things right, your colors won't be right.

These examples have comment nodes in them to help you figure out the RGB order.

(Does your neopixel have a separate White? Like RGBW? Then these examples aren't a complete solution. I didn't have one of those to test, so I don't know how to do the W part. Contact me via github mechanisms, or [via the xod forum](https://forum.xod.io/u/awgrover) and help me add instructions for that!)

Do you have at least 3 neopixels? Try the `neopixel-example-rgb-revelation`. As supplied, it thinks it will turn the first pixel Red, the second Green, and the third Blue. But, if your neopixels aren't in "RGB" order, the colors will be wrong. Fortunately, all you have to do is read the colors that do show up, look up the value in the table below, and set the `t` value for the `adafruitneopixel` node (see below). This example helps you test until you get it right.

Do you have only 1 neopixel? Try the `neopixel-example-rgb-revelation1pixel`. As supplied, it thinks it will turn the first pixel Off, then Red, then Green, and then Blue (and repeat). But, if your neopixels aren't in "RGB" order, the colors will be wrong. Fortunately, all you have to do is read the colors that do show up, look up the value in the table below, and set the `t` value for the `adafruitneopixel` node (see below). This example helps you test until you get it right.

#### The `t` value (RGB order)

Did I say "all you have to do is..."? Well, this prototype library makes you do the work of finding and using the right value for the `t` for the `adafruitneopixel` node.

(these values are from [Adafruit_NeoPixel.h file](https://github.com/adafruit/Adafruit_NeoPixel/blob/master/Adafruit_NeoPixel.h), the section that starts with `#define NEO_RGB`)

* From running the "revelation" example above, get the order of colors that actually showed for you, then find them in this table:

```
Red Green Blue      6
Red Blue Green      9
Green Red Blue      82
Green Blue Red      161
Blue Red Green      88
Blue Green Red      164
```

* Use the number shown as `t`.

### Adafruit Library Example: "simple" -- light pixels in order

It was easier to repeat the pattern. But, quite close to the original example.

### Adafruit Library Example: "simple\_new\_operator"

This is the same as above, but using "new" in c++. Not relevant for XOD.

### Adafruit Library Example: "strandtest" -- several patterns

The automatic conversion of the library skipped `setBrightness()`, which this uses. It skipped it because the signature (declaration) in .h is: `void setBrightness(uint8_t)`, and the argument has no name. `fill()` is also skipped, possibly because of the default values for the arguments? This is acting like an inherent limitation of the `cindex` interface to `libclang`. 

So, I didn't write these examples.

I could just be doing it wrong.

# Playing With My Converter

Yikes! It's a hack! clanglib -> python bindings -> python program -> perl. 

Super terse instructions: change `/home/awgrover` as appropriate. Only works on ubuntu linux (lots of hard coded paths inside).

* Built on Ubuntu 16.04. Expects that a lot.
  * `apt-get libclang1-3.8 python2.7 perl`
  * `sudo pip install clang==3.4` # (whatever your clang --version is!)
  * `sudo cpan Text::Template`
  * The Arduino IDE is useful for fetching arduino libraries
* Edit `ard2xod`, find all the hardcoded paths and fix them (not nice!).
  * Those need to be automated, and/or allowed in the .config
* Fetch an Arduino library. I often use the Arduino IDE.
* Fill in useful values for .config: 
  * `./ard2xod config > .config`
  * edit that, remove the comment, fill in values
* make the lib:
  * This will create it in your `xod/__lib__` directory.
  * Find the directory that has the Arduino Library's `.h` and `.cpp`, for me it was:
  * `./ard2xod make /home/awgrover/Arduino/libraries/Adafruit_NeoPixel`

# Status

This is a prototype: it just barely works. it is poorly tested. mortals are likely to suffer if they get to close to it. professionals should take precautions.

So much to fix/change/figure out. Tracking it in the dev-nodes.md document.

