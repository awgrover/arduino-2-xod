
# ard2xod: automatic conversion of Arduino libraries to XOD libraries

Mechanically convert Arduino IDE libraries to XOD libraries.
 
It requires a degree of c++ expertise to make [Arduino IDE libraries](https://www.arduino.cc/en/Guide/Libraries) [usable in XOD](https://xod.io/docs/guide/wrapping-arduino-libraries) (at least up till ([~ v0.25.2 2018-11-06](https://xod.id) ). This is quite a barrier to using XOD for many projects. For example, XOD did not have the full NeoPixel library (@bradzilla84 has a [partial one](https://xod.io/libs/bradzilla84/neopixel/)!), and Neopixels are very popular.

This tool makes it possible to generate a XOD library from an Arduino library. The class in the Arduino library becomes a [`custom type`](https://xod.io/docs/guide/custom-types), produced by a constructor patch, and each method becomes a patch. The result is expected to be a bit crude, and low-level, but usable. 

# Status

This tool is still rough. If you give me feedback, I can improve it.

* Poorly tested, on a few libraries.
* Has only been used on Ubuntu 16.04
* Several limitations from the `cindex` interface of `libclang`:
  * Skips some methods arbitrarily (e.g. if an argument has no formal parameter name).
  * Skips methods if the return type, or any argument type can't be converted to XOD via my table `%cpp2xod_type` (in `ard2xod`). Only knows scalar types.
  * `char *`, `void *`, function pointers, classes, structs, etc. are not handled.
* I keep breaking things as I work on this (see "poorly tested" above). Generating as a library (as opposed to a project) is broken.
* Numeric values have size/range issues. XOD only has "number" and "byte". So, unsigned isn't signalled, truncation/overflow can happen, etc. I think that int32's are larger than XOD "number".
* Since I `emit` the return value of a method, and I always emit the instance, you may get redundant outputs for the instance. e.g.:
    `PubSubClient& setServer(uint8_t  ip)`
  * Would emit the instance, some instance of PubSubClient, which might be the same instance (which is hard to tell).
* Since it's difficult to deduce, I assume all methods are `impure`, and therefor need a `trigger` input to make them `fire`.
* I skip public instance-variables, because I don't know what to do with "set". I just haven't got to doing "get".
* Enums are not converted. Mostly waiting on [XEN-F001](https://forum.xod.io/t/xen-f001-enums/1208/9).
* The `dev-notes.md` file has an indication of known issues, intentions.

# Install

## Ubuntu 16.04

* checkout this git project, or download the .zip
  * both `ard2xod` and `dump_ast.py` need to be executable.
* `apt-get libclang1-3.8 python2.7 perl`
* `sudo pip install clang==3.8` # (whatever your `clang --version` is!)
* `sudo cpan Template::Toolkit`
* The Arduino IDE is useful for fetching arduino libraries.

Setup:

* Fill in useful values for .config:
  * `./ard2xod config > .config`
  * edit that
  * delete `key:values` that look right (since they are getting deduced correctly)
  * figure out values that are wrong/incomplete

# Usage

* Download an Arduino library. e.g.:
  * checkout a git project from github
  * download the .zip from github and unzip it to a directory
  * use the Arduino IDE to "install" a library, find your Arduino libraries directory (`~/Arduino/libraries/` on my linux).
* I recommend creating a XOD project from the Arduino library:
    `./ard2xod make --project that/arduinolibrary/directory`
  * The directory should have a `library.properties` file in it, and the `.h` (or `src/.h`).
  * Here's an example:
    `./ard2xod make --project /home/awgrover/Arduino/libraries/Adafruit_NeoPixel`
* Watch the verbose output for obvious errors.
* Open the project in XOD
  * Open the "readme" patch, check the warnings
  * Compare the patches to the list of methods in the original `.h`
  * Add/edit things that aren't right or are missing.
  * (re-)write the examples to test the conversion.
  * File an `issue` with this [github project](https://github.com/awgrover/arduino-2-xod), or send a message via [XOD Forum Messages](https://forum.xod.io/u/awgrover), or post on the [XOD Forum](https://forum.xod.io/) if there are problems.
* Publish your work as a XOD library.

# Generated Library (Using the Patches)

The tool gets the library name from `library.properties`, and uses that as the XOD library name, and the name of the `.h` file. Then a `-ll` is appended to indicate "low-level". The name may not be the same as the Arduino library directory! e.g.: [ViSi-Genie-Arduino-Library](https://github.com/4dsystems/ViSi-Genie-Arduino-Library) has the `name` "genieArduino".

The first class in the `.h` file is assumed to be the class of interest. It is used for the name of the constructors, and the `custom-type`.

The tool should generate a patch for each constructor, which emits the instance.

Each method is assumed to be `impure` (see [discusson](https://forum.xod.io/t/objects-xod-chaining-best-practices/1524/7)). So, each method takes a `trigger` pulse to make it fire. And, emits a `done` pulse. This is one of the things you might change (for select patches) after generating the XOD library.

At some point in your XOD program, you may need to generate a pulse, but you've only calculated a value. E.g. update a neopixel based on a counter. You could use `pulse-on-change`. But, if you need a pulse on every emit (regardless of value change), then there is no native XOD patch that can do that (that I know of). I've written a "data-to-pulse" patch for that, [awgrover/conversions/data-to-pulse](https://xod.io/libs/awgrover/conversions/data-to-pulse/).

I seem to think it is convenient for each method to emit the instance.

# Goals

Make libraries available faster, and without needing c++ expertise.

The conversion should generate a library that is obviously associated with the Arduino library. Then XOD users have a good chance of finding it, and knowing what it does. But, also indicate that it may be a bit rough. 

The conversion should provide most features, and a XODer could then edit it, or make a prettier library around it. If the tool only gets 80% right, that's probably good enough to use for many things (and can be manually repaired later). So, automatic conversion can make libraries available faster, and more accessible.

The conversion should be parallel to the Arduino library, then existing tutorials for the Arduino IDE world would still be usable, and give some idea of working in XOD.

Credit the original library.

Provide this conversion tool as a utility (and process) for the XOD community, built into XOD or via the XOD website. A XODer that does the initial conversion should be able to engage other XODers easily to fix & improve a conversion.


