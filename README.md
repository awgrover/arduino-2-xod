# BUG
put some bad stuff in a lib, get red error notice
ERROR. The error has no formatter. Report the issue to XOD developers.
Nothing relevant in dev tools. maybe a Error: ENOENT: no such file or directory, open '/opt/XOD IDE/resources/app-update.yml'
 

# Automatic XOD Library from Arduino Library

Up till now ([XOD](https://xod.id) v0.25.2 2018-11-06), it has required a degree of expertise to make [Arduino IDE libraries](https://www.arduino.cc/en/Guide/Libraries) [usable in XOD](https://xod.io/docs/guide/wrapping-arduino-libraries). This is quite a barrier to using XOD for many projects. For example, XOD does not have the NeoPixel library, and Neopixels are very popular.

## Hypothesis

It ought to be possible to parse the .h file of a typical Arduino Library and produce a low-level XOD library automatically: a class node, and accessor/method nodes. Cf. [Wrapping Class-based Arduino Libraries](https://xod.io/docs/guide/wrapping-arduino-libraries/).

This should give a typical XOD user a good chance of just using the new XOD nodes, in a way parallel with the documentation/tutorials that come with that Arduino IDE library.

A high-level (normal user) library can also be built on top of that, purely in XOD. That should expand the pool of contributors, and make high-level node-libraries more common.

## Example: NeoPixel

Using as an example throughout, the Adafruit [NeoPixel V1.1.7 library](https://github.com/adafruit/Adafruit_NeoPixel) library. Github based libraries are the easiest.

## Problems

This approach would have problems if the library does anti-social things like:

* open the serial port (surprisingly common)
* use `delay()`
* open Wire
* acquire other resources

A non-github library could be used: the user could download it (or install it in the Arduino IDE).

How would you handle "asynch" actions?

## Library = Library

- [x] Use the `author` from the Arduino IDE `library.properties`
- [x] Use the directory name as the Arduino IDE library (so it's parallel with Arduino)
- [x] Create a new XOD project `~/xod/__lib__/$author/$directory`
-- restricting name to 0-9a-z-
- [x] Other information from the `library.properties` goes in `project.xod`
- [x] shows up in xod

`./ard2xod library /home/awgrover/Arduino/libraries/Adafruit_NeoPixel`

### Neopixel example

* Arduino IDE lib: `~/Arduino/libraries/Adafruit_NeoPixel`
* XOD library: `~/xod/__lib__/Adafruit/Adafruit_NeoPixel`

File `~/Arduino/libraries/Adafruit_NeoPixel/library.properties `

    name=Adafruit NeoPixel
    version=1.1.7
    author=Adafruit
    maintainer=Adafruit <info@adafruit.com>
    sentence=Arduino library for controlling single-wire-based LED pixels and strip.
    paragraph=Arduino library for controlling single-wire-based LED pixels and strip.
    category=Display
    url=https://github.com/adafruit/Adafruit_NeoPixel
    architectures=*

File `~/xod/__lib__/adafruit/adafruit_neopixel/project.xod` (nb. lower case):

    {
       "name" : "Adafruit NeoPixel",
       "description" : "Arduino library for controlling single-wire-based LED pixels and strip.\nArduino library for controlling single-wire-based LED pixels and strip.",
       "version" : "1.1.7"
    }

Deduce license?
- [ ] version doesn't show in XOD
-- make a readme patch

## Libary Class = Node w/State and Bus

Most libraries are built around a c++ class. XOD now has "state" for the c++ nodes; and "bus" nodes. This maps better to the class/instance pattern of typical Arduino IDE libraries.

### Parsing

LLVM/Clang has c++ parser that is [externally accessible](http://clang.llvm.org/docs/IntroductionToTheClangAST.html), that should give us the ability to pick out the class, constructors, and public methods of an Arduino IDE library. The clang AST interface has [issues](https://foonathan.net/blog/2017/04/20/cppast.html). Maybe use [python cmonster](https://github.com/axw/cmonster), or [cppast](https://foonathan.net/blog/2017/04/20/cppast.html). 

Getting the full AST is problematic. However, several language bindings to the "index" ast are available, and that seems sufficient for this proof. Being able to parse the actual .cpp code would allow detecting delay(), Serial.x, etc.

*problems* The reported ast seems to omit some methods (e.g. fill() is not reported in Adafruit_Neopixel); the type doesn't seem to indicate the correct size or "unsigned" (uint8_t is reported the same as uint16_t).

- For each constructor:
- [x] Turn the main class into a patch $classname (+ '2' for 2nd etc.)
-- patches are lower case, "-" only
- [x] has constructor args as inputs of right type, 
- [x] and has a "self" output. (we need to know that xod type...)
-- for first constructor, the patch name is the xod-type: @/adafruit-neopixel, aka @/output-adafruit-neopixel
-- second constructors get a "self" output of that type, not xod-self
- with a .cpp   
- [x] that holds the state

`./ard2xod constructor /home/awgrover/Arduino/libraries/Adafruit_NeoPixel /home/awgrover/xod/__lib__/adafruit/adafruit-neopixel`

- For each public method
- [x] "this" is `"type": "@/input-adafruit-neopixel"`
- [x] return this is `"type": "@/output-adafruit-neopixel"`
- [ ] pointer types (return): uint8 * getPixels()
-- convert that to a ref type, provide utils?
- [ ] pointer types (args)
- [ ] unnamed args: sine8(uint8_t) const,
- [ ] skip statics

./ard2xod methods /home/awgrover/Arduino/libraries/Adafruit_NeoPixel /home/awgrover/xod/__lib__/Adafruit/Adafruit_NeoPixel`

- For each public attribute
- [x] "this" is `"type": "@/input-adafruit-neopixel"`

./ard2xod properties /home/awgrover/Arduino/libraries/Adafruit_NeoPixel /home/awgrover/xod/__lib__/Adafruit/Adafruit_NeoPixel`

** adafruit-neopixel1/ crashes xod
** doing protected properties for demonstration

rm -rf /home/awgrover/xod/__lib__/adafruit/adafruit-neopixel; ./ard2xod library $ard $xod; ./ard2xod constructor $ard $xod

*support* nodes (generics)
Apparently I'll need to make instances of "generic" nodes like 'if': `Cannot find specialization gate(adafruit-neopixel) for abstract xod/core/gate.`
- [x] Instead, emit object & pulse

set-pixel-color: done=>pulse
get-pixel-color: val=>int
### Neopixel example

File `Adafruit_NeoPixel.h`

    class Adafruit_NeoPixel {
        ...
        Adafruit_NeoPixel(uint16_t n, uint8_t p=6, neoPixelType t=NEO_GRB + NEO_KHZ800);
        Adafruit_NeoPixel(void);
        ...
        }

Patch Adafruit_NeoPixel

CODE HERE annotate as a template


## Methods/Accessors: Actions and Values

Each method (and public attribute) becomes a patch.

- [x] At least an input for the object.
-- [x] if it has void return value, add a "pulse" output "trigger".

? attributes can be updated by methods, or represent hardware inputs, which need to trigger "update" in the xod graph.

### Neopixel example

File `Adafruit_NeoPixel.h`

    class Adafruit_NeoPixel {
        ...
    void
        begin(void),
        show(void),
        setPin(uint8_t p),
        setPixelColor(uint16_t n, uint8_t r, uint8_t g, uint8_t b),

### issues

* XOD has a port type, but library code typically uses int or uint.

# Discuss

* First valid library: emitted a pulse on most nodes. Found that I wanted to chain things (for sequencing), and wanted the object.

* get compile error: the 'label' of the xod/patch-nodes/output-self is actually used in the cpp (possibly a bug: failed to globally s/-/_/ ?):
```
    namespace xod {

    //-----------------------------------------------------------------------------
    // adafruit/xneo/adafruitneopixel implementation
    //-----------------------------------------------------------------------------
    namespace adafruit__xneo__adafruitneopixel {

    //-- constructor Adafruit_NeoPixel(n, p, t)
    //#pragma XOD require "https://github.com/adafruit/Adafruit_NeoPixel"

    // Include C++ library:
    // --- Enter global namespace ---
    }}
    #include <Adafruit_NeoPixel.h>

    namespace xod {
    namespace adafruit__xneo__adafruitneopixel {
    // --- Back to local namespace ---
    // Our namespace should be: adafruit__adafruit_neopixel__adafruit_neopixel
    // Reserve the space for the object.
    struct State {
      uint8_t mem[sizeof(Adafruit_NeoPixel)];
    struct Node {
        State state;
        adafruit__xneo__adafruitneopixel::Type output_adafruit-neopixel;

        union {
            struct {
                bool isOutputDirty_adafruit-neopixel : 1;
                bool isNodeDirty : 1;
            };

            DirtyFlags dirtyFlags;
        };
    };
```
* possibly similar bug to above. I think the synthetic adafruit/adafruit-neopixel/output-adafruit-neopixel is all "-", so in xodp:
"type" : "adafruit/adafruit-neopixel/output-adafruit-neopixel"
but, in several places in the transpiled code:
```
struct Node {
    State state;
    adafruit__adafruit_neopixel__adafruit_neopixel::Type output_adafruit-neopixel;
    Logic output_done;

    union {
        struct {
            bool isOutputDirty_adafruit-neopixel : 1;
```
So, again, failure to globally s/-/_/ ?

* I think "patch name is type name" is mostly true, but failure to s/-/_/g.

# More Automation

To make this usable by a normal person, there should be some automation for getting the library:

* Choose whether to make a library, or just a project?
* Let this process use the libraries installed in the Arduino IDE.
* Use the same "Manage Libraries" protocol to fetch Arduino IDE libraries.
* Provide a "get from github" search/install interface.
* `#pragma XOD require "https://github.com/adafruit/Adafruit-PN532"` lines?
* How can we get the license? Via the 'url' key?
* While "importing" a library, or just after, let the user rename arguments and types (e.g. "uint_16 p" to "port port")
* Fixup code with with options like "once only" -> "if (!isSettingUp()) return;"
* Use common inline doc comments as descriptions for xod

- [ ] want to double-click make comment. '//'
- [ ] want to style comments to make sections 
- [ ] a library should have a readme? or are examples good enough?
- [ ] slow startup: reading "libs"? needs spinner. can stuff be cached?
- [ ] add prominent examples like the ard ide: especially blink, or "get board info" or something
- [ ] can't get back to tutorial w/o restart?
- [ ] the "console"(?) (the deploy text section at bottom) doesn't auto-position at bottom, often have to scroll to bottom manually
- [ ] convert to bus should ask for name. using  the node-name as default?
- [ ] the label for from-bus should validate the name, possible drop-down, or some way of getting it right (most recent)
- [ ] renaming a to-bus should rename all from-bus that are currently the same
- [ ] Instructions for manually installing arduino libs isn't quite right: ~/xod/__ardulib__/$arduinolibrary

