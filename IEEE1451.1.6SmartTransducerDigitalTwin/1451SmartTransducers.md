# Python-Based Digital Twin Smart-Transducer Communication Testbench via MQTT

This folder is for IEEE 1451-based smart transducer (sensors and actuators) testbed, designed as a phyiscal twin for digital twin research. For more in depth information on the development process and usage of this project, reference the **technical document**.

Note: During testing, a local network was created between a laptop (Linux based, hosting the Mosquitto MQTT client and APP) and a Rasberry Pi (carrying the smart sensor/actuator). The MQTT broker was run on this network.  
The laptop was ensured to have the correct local IP address with every boot of the system by using these two commands in the command line:
```shell
sudo ip addr add 192.168.1.33/24 dev enp0s31f6
sudo ip route add default via 192.168.1.1
```

## Use
Download all "---_pubsub" python scripts from this folder. **In each script, change the IP address in the 'MQTT Client Setup' section to the correct one for your MQTT broker**.  

To run the testbench, first ensure that the MQTT broker is running. Then, start each script using the format below (order should not matter). If multiple clients are running on the same device, run their respective scripts in different terminals. If there are no execution errors, their first print to stdout should be "Connected with error code 0."
```shell
python3 example_pubsub.py
```

## Tesing/Debugging
Windows where the scripts are invoked become **debug panels** for their respective clients. They will display all messages published by and forwarded to the topics that the client is subscribed to.  

If a **physical display** of temperature sensor readings is desired, download the script meant for the LCD1602 module.


## Author
Tyler Wong  
Department of Electrical and Computer Engineering  
University of Maryland, College Park
