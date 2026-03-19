#!/usr/bin/python
import os
import glob
import paho.mqtt.client as mqtt
import time
import json
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

appId = "041000002700004D00000007E90000000000"
rpiId = "041000002700004D00000107E90000000000"
sensorId = "041000002700004D00000207E90000000000"
servoId = "041000002700004D00000307E90000000000"

sensorreq = { # sensor data request
  "netSvcType" :  2, # transducer access services
  "netSvcId" : 1, # read from channel of TIM
  "msgType" : 1, # command
  "msgLength" : 78, # bytes
  "appId" : appId,
  "ncapId" : sensorId,
  "timId" : rpiId,
  "channelId" : 1,
  "samplingMode" : 5, # continuous
  "timeout" : 60,
}

servoreq = { # actuator movement request
  "netSvcType" : 2, # transducer access services
  "netSvcId" : 7, # write to channel of TIM
  "msgType" : 1, # command
  "msgLength" : 78, # bytes
  "appId" : appId,
  "ncapId" : servoId,
  "timId" : rpiId,
  "channelId" : 1,
  "samplingMode" : 5, # continuous
  "timeout" : 60,
}

time_values = []
temp_values = []
start_time = time.time()

def update_plot():
  unit = time_unit.get()
  if unit == "minutes":
    x_data = [t / 60 for t in time_values]
    ax.set_xlabel("Time (min)")
  elif unit == "seconds":
    x_data = time_values
    ax.set_xlabel("Time (sec)")
  
  line.set_data(x_data, temp_values)
  ax.relim()
  ax.autoscale_view()
  _, xmax = ax.get_xlim()
  ax.set_xlim(left=0, right=max(x_data)*1.05 if x_data else 1)
  canvas.draw()

def send_sensorreq():
  curr_time = round(time.time() - start_time, 3)
  client.publish("_1451.1.6/D0/SMARTSENSOR", json.dumps(sensorreq))
  print(">Published request '{json.dumps(sensorreq)}' to topic '_1451.1.6/D0/SMARTSENSOR'")
  # update textbox
  text_box.config(state='normal')
  text_box.insert(tk.END, f"{curr_time:.3f}s: Smart sensor request published.\n")
  text_box.config(state='disabled')

def periodic_sensor_request():
    send_sensorreq()
    root.after(10000, periodic_sensor_request)  # Call again in 10 seconds

# when connected with broker
def on_connect(client, userdata, flag, rc):
  print(">Connected with result code " + str(rc))
  client.subscribe("_1451.1.6/D0/SMARTSENSOR")
  client.subscribe("_1451.1.6/D0/SMARTACTUATOR")
  
# when disconnected with broker
def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print(">Unexpected disconnection. Trying to reconnect:")
    while(1):
      try:
        client.reconnect()
        print(">Reconnected.")
        break
      except:
        print(">Reconnect failed, retrying in 5s:")
        time.sleep(5)

# when received messages
def on_message(client, userdata, msg):
  payload = json.loads(msg.payload)
  curr_time = round(time.time() - start_time, 3)
  if payload["msgType"] == 2: # response
    print(">Received response '" + str(payload) + "' on topic " + msg.topic)
  
    if bytes.fromhex(payload["ncapId"]) == bytes.fromhex(sensorId): # sensor response, compare as 16-byte values
      curr_temp = payload["transducerSampleData"]
      temp_values.append(float(curr_temp))
      time_values.append(curr_time)
      
      text_box.config(state='normal')
      text_box.insert(tk.END, f"{curr_time:.3f}s: Smart sensor data received: {float(curr_temp):.3f} C")
      if float(curr_temp) >= 27:
        client.publish("_1451.1.6/D0/SMARTACTUATOR", json.dumps(servoreq))
        print(f">Published request '{json.dumps(servoreq)}' to topic '_1451.1.6/D0/SMARTACTUATOR'")  
        text_box.insert(tk.END, " --> Smart actuator write request published.")
      text_box.insert(tk.END, "\n")
      text_box.config(state='disabled')

      update_plot() # update graph
    
    if bytes.fromhex(payload["ncapId"]) == bytes.fromhex(servoId): # actuator response, compare as 16-byte values
      text_box.config(state='normal')
      text_box.insert(tk.END, f"{curr_time:.3f}s: Smart actuator write confirmation received.\n")
      text_box.config(state='disabled')

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect= on_disconnect
client.on_message = on_message
client.connect("192.168.1.33", 1883, 60)
client.loop_start()

# GUI setup
root = tk.Tk()
root.title("Smart Transducer Digital Twin Testbed | NIST")
root.resizable(False, False)
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

text_frame = ttk.Frame(frame) # text box
text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_box = tk.Text(text_frame, height=40, width=90)
text_box.config(state='disabled')
text_box.pack(padx=(10,5), pady=(10,1), fill=tk.BOTH, expand=True)

plot_frame = ttk.Frame(frame) # temp data plot
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
time_unit = tk.StringVar(value="seconds") # time unit select dropdown
unit_menu = ttk.OptionMenu(plot_frame, time_unit, "seconds", "seconds", "minutes", command=lambda _: update_plot())
unit_menu.pack(padx=10, pady=(10,1), anchor='e')
fig, ax = plt.subplots(figsize=(8,3))
line, = ax.plot([], [], marker = 'o')
ax.set_title("Temperature vs Time")
ax.set_xlabel("Time (sec)")
ax.set_ylabel("Temperature (C)")
ax.axhline(y=27, color='red', linestyle='--', linewidth=1.5) # threshold line
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=(5,10), pady=(1,10))

btn = tk.Button(text_frame, text="Publish sensor data request!", command=send_sensorreq, height=2, width=25) # pub button
btn.pack(pady=(1,10), anchor='center')

# Start periodic looping 1 second after GUI starts
root.after(1000, periodic_sensor_request)

root.mainloop()
