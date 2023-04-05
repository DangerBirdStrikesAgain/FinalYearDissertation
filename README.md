Welcome to my Part II Project, A MANET to Facilitate Collision Avoidance in Rowing Boats. This is a repository containing all my code, including all the strange and wonderful experimentation I conducted to get to the final product.

</br>
 
# **Guide to creating your own MANET to facilitate collision avoidance in Rowing Boats**
This is a 'how to' guide to building the nodes and downloading the software needed to build your very own MANET. Each node *should* beep (or flash an LED, depending on what you choose) when the user is approaching a known obstacle, much like parking sensors on a car! A disclaimer - I do not guarantee this will work and take no responsibility for any collisions.

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

## Tools Needed
- Soldering iron
- Drill and bit of the same diameter as your button (I use 12mm)