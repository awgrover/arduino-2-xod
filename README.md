# Automatic XOD Library from Arduino Library

# Summary and Usage

Up till now ([XOD](https://xod.id) v0.25.2 2018-11-06), it has required a degree of expertise to make [Arduino IDE libraries](https://www.arduino.cc/en/Guide/Libraries) [usable in XOD](https://xod.io/docs/guide/wrapping-arduino-libraries). This is quite a barrier to using XOD for many projects. For example, XOD does not have the NeoPixel library (@bradzilla84 has a [partial one](https://xod.io/libs/bradzilla84/neopixel/)!), and Neopixels are very popular.

I thought it would be possible to automatically generate a XOD library from an Arduino library. The class in the Arduino library becomes the "object" in XOD via the constructor, and each method becomes a node. 

I assumed that the result might be a bit crude, and low-level. But, it provides all the features, and a XODer could then make a prettier library around it. If it only gets 80% right, that's probably good enough to use for many things (and can be manually repaired later). So, automatic conversion could make libraries available faster, and more accessible.

Also, if the XOD library were parallel to the Arduino library, then existing tutorials for the Arduino IDE world would give some idea of how to use them in XOD.

My vision is to see this installed in XOD itself, or in the XOD website. We could build up the libraries quite quickly. As they are auto-converted, we should request refinement/repair/wrapping on the XOD forum!

I chose Adafruit's [NeoPixel V1.1.7](https://github.com/adafruit/Adafruit_NeoPixel) library to try.

# Playing With The Auto-converted Neopixel Library

I did not upload it, because it likely has many issues. Also, not really ready for beginners! But you could still try.

The library has the philosophy that you "thread" the patches together with the "object" (the output of the constructor), to get patches to fire in the right order. I think the XOD team prefers a different philosophy (this is another post for discussion!). Anyway, this prototype works like that.

* Manually install the library from [github](https://github.com/awgrover/arduino-2-xod). Back to the stone age:
  * Download the zip (from "download or clone")
  * Using your archive extractor (i.e. open the .zip), find the `xod/__lib__/adafruit` directory
  * Copy the directory into your `$xoddir/__lib__`. On linux it's `~/xod/__lib__`, sadly I don't know what it is on windows or mac. Sorry.
  * quit and restart XOD
  * You should have the new library!
* Example
   * I have one example built! In the zip you downloaded above, it's `xod/neotest6.xodball`. Copy it into your xod directory, or just put it somewhere and open it directly from xod (or import it). It shows setting 2 pixels, with a delay between them.
* Basic usage. Very much like the Arduino IDE.
  * "make" the neopixel object
    * Use the `adafruitneopixel` patch to represent a single neopixel "string". Actually, I suppose, it represents "all the neopixels on the same wire on a particular pin". Because you can chain neopixel devices together.
    * `n` is the number of "pixels" in the string.
    * `p` is the pin the string is on. Just like for the Arduino IDE, most digital pins work.
    * `t` is the RGB order. My neopixel happens to be GRB. Sadly, you have figure this out and use the right value. See "Example: Figure out RGB order" below! You can start with '6' to get going, but your colors may be wrong.
  * Put the `begin` patch in, and link.
  * Now add various patches like `set-pixel-color`, chaining together via the `dev` outputs.
    * Don't forget `show`! Just like in the Arduino IDE.
    * The "methods" from Arduino IDE are patches in XOD.

## Properties

As a demonstration, I converted instance-variables to nodes. This is to be discussed! You don't actually want to use them, because they are actually private, and won't work. Look for "property" in the description.

## Examples

I'm working on more examples, copying the Arduino [library's examples](https://github.com/adafruit/Adafruit_NeoPixel/tree/master/examples). That will be a good further test of what I've done. I'll update my github xod library as I go and add to this thread. Look for examples in [xod/](https://github.com/awgrover/arduino-2-xod/tree/master/xod) in my [github](https://github.com/awgrover/arduino-2-xod).

Examples are in the xod library as patches.

### Example: "revelation" -- Figure out RGB order

(these 2 examples are in the github stuff `xod/` directory. Yes, they should be in the library, but there were some annoyances. You can directly open the `.xodball` after you've downloaded the zip from github, and extracted all the `.xodball`'s.)

Apparently, neopixels come in many flavors: they aren't all in the obvious RGB order. `set-pixel-color' takes a red, green, and blue argument, but if you haven't set things right, your colors won't be right.

Not from the Adafruit library, but seem very useful to me. These examples have comment nodes in them to help you figure out the RGB order.

(Does your neopixel have a separate White? Like RGBW? Then these examples aren't a complete solution. I didn't have one of those to test, so I don't know how to do the W part. Contact me via github mechanisms, or [via the xod forum](https://forum.xod.io/u/awgrover) and help me add instructions for that!)

Do you have at least 3 neopixels? Try the `neopixel-example-rgb-revelation`. As supplied, it thinks it will turn the first pixel Red, the second Green, and the third Blue. But, if your neopixels aren't "RGB", the colors will be wrong. Fortunately, all you have to do is read the colors that do show up, look up the value in the table below, and set the `t` value for the `adafruitneopixel` node (see below). This example helps you test until you get it right.

Do you have only 1 neopixel? Try the `neopixel-example-rgb-revelation1pixel`. As supplied, it thinks it will turn the first pixel Off, then Red, then Green, and then Blue. But, if your neopixels aren't "RGB", the colors will be wrong. Fortunately, all you have to do is read the colors that do show up, look up the value in the table below, and set the `t` value for the `adafruitneopixel` node (see below). This example helps you test until you get it right.

#### The `t` value (RGB order)

Did I say "all you have to do is..."? Well, this prototype library makes you do the work of finding and using the right value for the `t` for the `adafruitneopixel` node.

(these values are from [Adafruit_NeoPixel.h file](https://github.com/adafruit/Adafruit_NeoPixel/blob/master/Adafruit_NeoPixel.h), the section that starts with `#define NEO_RGB`)

* From running the "revelation" example above, find the order of colors that actually showed for you in this table:
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

# Playing With My Converter

Yikes! It's a hack! clanglib -> python bindings -> python program -> json -> perl. 

Super terse instructions: change `/home/awgrover` as appropriate. Only works on ubuntu linux (lots of hard coded paths inside).
* create the xod library directory (tells you the xod library path): `./ard2xod library /home/awgrover/Arduino/libraries/Adafruit_NeoPixel`
* make all the patches: `./ard2xod make /home/awgrover/Arduino/libraries/Adafruit_NeoPixel /home/awgrover/xod/__lib__/adafruit/adafruit-neopixel`
  
I'm going to work on the examples first. Bug me if you want more "how to" sooner.

# Status

This is a prototype: it just barely works. it is poorly tested. mortals are likely to suffer if they get to close to it. professionals should take precautions.

So much to fix/change/figure out. Tracking it in the dev-nodes.md document.

