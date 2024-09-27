# Bosch Car Augmented Reality Live Digital Twin
<img src="https://img.shields.io/badge/language-Python>=3.10-blue"/> <img src="https://img.shields.io/badge/language-Arduino C++-blue"/> <img src="https://img.shields.io/badge/platform-arenaxr.org-green"/> <img src="https://img.shields.io/badge/license-BSD 3 License-red"/> 

A demo showing a one-to-one mapping of a physical hardware component with a simulated digital twin. Here we see a toy car representing a common use case of machine maintenance and repair, and showing a live updated, real-time representation in a 3D virtual space overlaid in augmented reality.

The toy car detects its state using sensors read by an Arduino, which it updates to a computer running a Python script using serial communication, whereby the state is then streamed to it's cloud digital twin counterpart in arenaxr.org.

<img src="Images/Bosch_Car_Splash.gif" width="800"> 
*Augmented reality 3D scanned digital twin on left. Real physical hardware with human operator on right. 

Full video recorded on iPad Pro M2: https://www.youtube.com/watch?v=Dkri8WgtiOs*

<img src="Images/Bosch_Car_POV.gif" width="800"> 
*First person mixed reality view of digital twin next to physical toy car disassembly process. 

Full video recorded on Meta Quest 3: https://youtu.be/GraLLFCjwF0*

## Setup
Install package using pip ([https://pypi.org/project/arena-py/](https://pypi.org/project/arena-py/)):
```shell
pip3 install arena-py
pip3 install colorama
pip3 install pyserial

```

## How to use
Run the terminal command:

```shell
py BoschCar.py -mh "arenaxr.org" -n "johnchoi" -s "BoschCarArduino" -p 0 0 0 -r 0 0 0 -c 1 1 1

```
 -mh = host | -n = namespace | -s = scene | -p = position | -r = rotation | -c = scale

<img src="Images/Bosch_Car_Arena.png" width="800"> 
Scene link to digital twin: https://arenaxr.org/johnchoi/BoschCarArduino

*Note: Make sure that an Arduino Nano with `Bosch_Car.ino` loaded with the correct serial port name is attached! By default, the serial port name is `COM3` on Windows. Make sure to change line 19 in `BoschCar.py` with the correct serial port name for your computer.*

## Parts
### Amazon
|Part|Link|Image|
|-----------|-----------|-----------|
|Theo Klein Bosch Car Toy|https://www.amazon.com/Theo-Klein-Bosch-Service-Engine/dp/B01CML4NFM/|<img src="Images/Parts/Amazon/BoschCar.jpg" width="200">|
|Automotive UHB Tape 0.4in|https://www.amazon.com/Double-Mounting-Waterproof-Length-Decor/dp/B08JG17H47/|<img src="Images/Parts/Amazon/UHBTape.jpg" width="200">|
|Lead Free Solder|https://www.amazon.com/Dia0-032in-0-11lb-Precision-Electronics-Soldering/dp/B07Q167J98/|<img src="Images/Parts/Amazon/Solder.jpg" width="200">|
|Arduino Nano with Shield Board|https://www.amazon.com/ALAMSCN-Nano-V3-0-ATmega328P-Controller/dp/B0BXKZQB1H/|<img src="Images/Parts/Amazon/ArduinoNano.jpg" width="200">|
|1/4in Automotive Loom Tube|https://www.amazon.com/YCLYC-Protectors-Protector-Electrical-Automotive/dp/B0C2BW13GG/|<img src="Images/Parts/Amazon/Loomtube.jpg" width="200">|
|3-pin PhotoResistors|https://www.amazon.com/Detection-Optical-Sensitive-Resistance-Photosensitive/dp/B099N5W9F7/|<img src="Images/Parts/Amazon/PhotoResistor.jpg" width="200">|
|16x2 LCD Display Module|https://www.amazon.com/GeeekPi-Character-Backlight-Raspberry-Electrical/dp/B07S7PJYM6/|<img src="Images/Parts/Amazon/LCD.jpg" width="200">|
|Perfboard|https://www.amazon.com/ELEGOO-Prototype-Soldering-Compatible-Arduino/dp/B072Z7Y19F/|<img src="Images/Parts/Amazon/Perfboard.jpg" width="200">|
|Multicolor Wire 22AWG|https://www.amazon.com/AWG-Stranded-Wire-Kit-Pre-Tinned/dp/B07T4SYVYG/|<img src="Images/Parts/Amazon/Wire.jpg" width="200">|
|Limit Switch|https://www.amazon.com/Twidec-Switch-Roller-Arduino-V-155-1C25/dp/B07NVD5LGM/|<img src="Images/Parts/Amazon/LimitSwitch.jpg" width="200">|
|Jumper Wires|https://www.amazon.com/Elegoo-EL-CP-004-Multicolored-Breadboard-arduino/dp/B01EV70C78/|<img src="Images/Parts/Amazon/Jumpers.jpg" width="200">|

### Pololu
|Part|Link|Image|
|-----------|-----------|-----------|
|0.100" (2.54 mm) Breakaway Male Header: 1×40-Pin, Straight, Black|https://www.pololu.com/product/965|<img src="Images/Parts/Pololu/0J6370.600x480.jpg" width="200">|
|0.1" (2.54mm) Crimp Connector Housing: 1x2-Pin 25-Pack|https://www.pololu.com/product/1901|<img src="Images/Parts/Pololu/0J1597.600x480.jpg" width="200">|
|0.1" (2.54mm) Crimp Connector Housing: 1x3-Pin 25-Pack|https://www.pololu.com/product/1902|<img src="Images/Parts/Pololu/0J1598.600x480.jpg" width="200">|
|0.1" (2.54mm) Crimp Connector Housing: 1x4-Pin 10-Pack|https://www.pololu.com/product/1903|<img src="Images/Parts/Pololu/0J1599.600x480.jpg" width="200">|
|0.100" (2.54 mm) Female Header: 1x2-Pin, Straight|https://www.pololu.com/product/1012|<img src="Images/Parts/Pololu/0J879.600x480.jpg" width="200">|
|0.100" (2.54 mm) Female Header: 1x4-Pin, Straight|https://www.pololu.com/product/1014|<img src="Images/Parts/Pololu/0J881.600x480.jpg" width="200">|
|Female Crimp Pins for 0.1" Housings 100-Pack|https://www.pololu.com/product/1930|<img src="Images/Parts/Pololu/0J2472.600x480.jpg" width="200">|
|Male Crimp Pins for 0.1" Housings 100-Pack|https://www.pololu.com/product/1931|<img src="Images/Parts/Pololu/0J2474.600x480.jpg" width="200">|

## Wiring Schematic
The wiring for the physical sensor hardware is very simple: it consists of just 4 photoresistor modules, 2 limit switches, and 1 LCD display for debugging, all connected to an Arduino Nano. Using a small perfboard or mini breadboard is recommended to organize the wiring:

<img src="Arduino/Fritzing/BoschCar_bb.png" width="600">

Arduino pin usage is as follows:
- VCC for power.
- GND for ground.
- A0 for Photoresistor 0 (Detect engine attached.)
- A1 for Photoresistor 1 (Detect hood open or closed.)
- A2 for Photoresistor 2 (Detect left wheel attached.)
- A3 for Photoresistor 3 (Detect right wheel attached.)
- A4 for SDA on LCD module (Shows status of all sensors.)
- A5 for SCL on LCD module (Shows status of all sensors.)
- D11 for Input Pullup Limit Switch (Detect left headlight attached.)
- D11 for Input Pullup Limit Switch (Detect right headlight attached.)

Here are some more useful diagrams of each module:

<img src="Arduino/Arduino-Nano-pinout-3.jpg" width="600">

**1602 LCD Display schematic:**

<img src="Arduino/LCD.jpg" width="600">

**Photoresistor schematic:**

<img src="Arduino/PhotoResistor.jpg" width="600">

## How to Build
Here is a step-by-step guide on how to build another one of these modified Bosch Cars with sensors for digital twins:

<img src="Images/Assembly/Portrait/done.jpg" width="800">

|0|Step Description|Image|
|-----------|-----------|------------------------------|
|1|First, create the wiring for the two limit switches. Since we are using the Input Pullup mode on Arduino to detect whether the switches are pressed or not, we only need two wires for each: signal and ground. Each wire should be around 16in long. Use heatshrink to cover the connectors and use 1/4in loom tube to wrap the wires nicely. Use 1x2 Crimp Connector Housings and Female Crimp Connectors.|<img src="Images/Assembly/Landscape/Limit_Switch.jpg" width="400">|
|2|Create the wiring for the four photo resistors. We need three wires for each: power, ground, and signal. Each wire should be around 18in long. Use 1x3 Crimp Connector Housings and Female Crimp Connectors on each end, and wrap the wires nicely with 1/4in loom tube.|<img src="Images/Assembly/Portrait/LoomWires.jpg" width="400">|
|3|Create a layout of headers and connectors on a breadboard or perfboard as shown in the wiring schematic above. Note the pin assignments, if they are different from the recommended mappings.|<img src="Images/Assembly/Portrait/Perfboard.jpg" width="400">|
|4|Hook up the Arduino Nano with prototyping shield to the breadboard or perfboard assembly using jumper wires.|<img src="Images/Assembly/Landscape/Arduino_Nano_Perfboard.jpg" width="400">|
|5|Hook up the cables for the photoresistors and limit switches to the breadboard or perfboard assembly.|<img src="Images/Assembly/Landscape/PartsElectronics.jpg" width="400">|
|6|Disassemble the Theo Klein Bosch toy car. Drill holes on the inside to cleanly route the loom tube cables throughout the chassis assembly.|<img src="Images/Assembly/Landscape/disassembled.jpg" width="400">|
|7|Route the loom tube cables through the Bosch toy car assembly. Use UHB automotive tape to fasten the photoresistors and limit switches onto the car assembly where appropriate. Two photo resistor should be at the top for the hood, one should be below the engine, and two should be at the sides below where the wheels attach, one for each side. The limit switches should be inside where the headlights click on.|<img src="Images/Assembly/Portrait/WireThrough.jpg" width="400">|
|8|When the wiring is complete and the sensors are attached, it is good to test the Python script and make sure everything works, before fastening the electronics board.|<img src="Images/Assembly/Portrait/Routing.jpg" width="400">|
|9|Finish the assembly by applying UHB automototive tape on the LCD screen, the perfboard/breadboard, and the Arduino Nano emplaced on the prototyping shield.|<img src="Images/Assembly/Landscape/wires_finished.jpg" width="400">|