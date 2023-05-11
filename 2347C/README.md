Welcome to my Part II Project, A MANET to Facilitate Collision Avoidance in Rowing Boats. This is a repository containing all my code, including all the strange and wonderful experimentation I conducted to get to the final product.

</br>

Repo Overview:
+ Development
    - The code that was used in development of the project
+ Evaluation 
    - The code used in evaluation of the project
+ OnDevice
    - **The interesting bit:** This is the code to put onto your device, the only part of this repo you need to run the system!
+ WriteUp
    - The dissertation and other parts of the project writeup

</br>
 
# **Guide to creating your own MANET to facilitate collision avoidance in Rowing Boats**
This is a 'how to' guide to building the nodes and downloading the software needed to build your very own MANET. Each node *should* beep (or flash an LED, depending on what you choose) when the user is approaching a known obstacle, much like parking sensors on a car! A disclaimer - I do not guarantee this will work and take no responsibility for any collisions.

</br>

## Components Needed
This is a list of what I used in my project, and therefore what the software I wrote has been designed for. Any microcontroller, GPS and radio can be substituted. 
- Raspberry Pi Pico
- Adafruit RFM69HCW Transceiver Radio Breakout
- Adafruit Ultimate GPS Breakout
- Non-latching Button (mine has an LED ring around it used to tell if the node is on)
- Buzzer and resistor (resistor moderates the pitch of the buzzer, I use 10k) 
- Waterproof box
- Power pack (to power the device)
- 3M Dual Lock or other method of attaching the final node to the boat
- Breadboard (optional but recommended)
- Wires

</br>

## Tools Needed
- Soldering iron
- Drill and bit of the same diameter as your button (I use 12mm)

</br>

## Wiring
![breadboard wiring](WriteUp\Dissertation\breadboard.jpg "Wiring for the breadboard on a virtual breadboard")

![wiring](WriteUp\Dissertation\wiring.jpg "Wiring diagram for the system")

</br>


## Software
After running CircuitPython on your device (AdaFruit has a good little tutorial here: https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython) 
Go to the OnDevice folder in this repository and upload the boot.py file and deviceCode.py to the Pico, then place the contents of the lib folder into the Pico's lib folder. When you're done, the Pico's filesystem should read:

```
boot.py
deviceCode.py

lib
    adafruit_gps.py
    rfm69.py
    config.py
```

You'll need to go into `lib > config.py` and manually set the `ADDRESS` constant to a unique value for each node. Remember each address must be smaller than 0xFE, 254!   

If you want to change any other parameters, they are all held in the config.py file, with comments above. Simply plug the device into your computer and edit. 

</br>

## SetUp 
As the button and any LEDs need to be on the outside of the box, you'll have to drill a hole into your waterproof box.  
![Button](WriteUp\Dissertation\button.jpeg "A button attached to the lid of a node being tested")

You'll now need to place the device into its waterproof box with a powerpack. I held all the components in place with dual lock to make sure they didn't move when inside the box. 
![Stick on velcro](WriteUp\Dissertation\sticky.jpeg "An image showing application of stick on velcro")

![Box all set up](WriteUp\Dissertation\insideBox.jpeg "An image showing all the components nestled safely inside their waterproof box")

![Attatched to boat](WriteUp\Dissertation\boxOnBoat.jpeg "The node places on the canvas of the stern of a single")

</br>

## Avoid accidents!
The device should work immediately on powerup. Row safely!