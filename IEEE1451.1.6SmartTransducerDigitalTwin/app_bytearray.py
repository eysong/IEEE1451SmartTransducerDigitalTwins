#!/usr/bin/python
import os
import time
import struct
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import paho.mqtt.client as mqtt

# appId = "041000002700004D00000007E90000000000"
# rpiId = "041000002700004D00000107E90000000000"
# sensorId = "041000002700004D00000207E90000000000"
# servoId = "041000002700004D00000307E90000000000"

# sensorreq = { # sensor data request
#   "netSvcType" :  2, # transducer access services
#   "setSvcId" : 1, # read from channel of TIM
#   "msgType" : 1, # command
#   "msgLength" : 61, # bytes
#   "appId" : appId,
#   "ncapId" : sensorId,
#   "timId" : rpiId,
#   "channelId" : 1,
#   "samplingMode" : 5, # continuous
#   "timeout" : 60,
# }

sensorreq = bytearray(65)
sensorreq[0] = 2 # netSvcType
sensorreq[1] = 1 # netSvcId
sensorreq[2] = 1 # msgType
sensorreq[3] = 61 # msgLength
sensorreq[4] = 0x04 # UUID appId 0
sensorreq[5] = 0x10 # 1
sensorreq[6] = 0x00 # 2
sensorreq[7] = 0x00 # 3
sensorreq[8] = 0x27 # 4
sensorreq[9] = 0x00 # 5
sensorreq[10] = 0x00 # 6
sensorreq[11] = 0x4D # 7
sensorreq[12] = 0x00 # 8
sensorreq[13] = 0x00 # 9
sensorreq[14] = 0x00 # 10
sensorreq[15] = 0x07 # 11
sensorreq[16] = 0xE9 # 12
sensorreq[17] = 0x00 # 13
sensorreq[18] = 0x00 # 14
sensorreq[19] = 0x00 # 15
sensorreq[20] = 0x04 # UUID ncapId 0
sensorreq[21] = 0x10 # 1
sensorreq[22] = 0x00 # 2
sensorreq[23] = 0x00 # 3
sensorreq[24] = 0x27 # 4
sensorreq[25] = 0x00 # 5
sensorreq[26] = 0x00 # 6
sensorreq[27] = 0x4D # 7
sensorreq[28] = 0x00 # 8
sensorreq[29] = 0x00 # 9
sensorreq[30] = 0x02 # 10
sensorreq[31] = 0x07 # 11
sensorreq[32] = 0xE9 # 12
sensorreq[33] = 0x00 # 13
sensorreq[34] = 0x00 # 14
sensorreq[35] = 0x00 # 15
sensorreq[36] = 0x04 # UUID timId 0
sensorreq[37] = 0x10 # 1
sensorreq[38] = 0x00 # 2
sensorreq[39] = 0x00 # 3
sensorreq[40] = 0x27 # 4
sensorreq[41] = 0x00 # 5
sensorreq[42] = 0x00 # 6
sensorreq[43] = 0x4D # 7
sensorreq[44] = 0x00 # 8
sensorreq[45] = 0x00 # 9
sensorreq[46] = 0x01 # 10
sensorreq[47] = 0x07 # 11
sensorreq[48] = 0xE9 # 12
sensorreq[49] = 0x00 # 13
sensorreq[50] = 0x00 # 14
sensorreq[51] = 0x00 # 15
sensorreq[52] = 1 # channelId 0
sensorreq[53] = 0 # 1
sensorreq[54] = 5 # samplingMode 0
sensorreq[55] = 0x00 # timeout 0
sensorreq[56] = 0x3C # 1
sensorreq[57] = 0 # 2
sensorreq[58] = 0 # 3
sensorreq[59] = 0 # 4
sensorreq[60] = 0 # 5
sensorreq[61] = 0 # 6
sensorreq[62] = 0 # 7
sensorreq[63] = 0 # 8
sensorreq[64] = 0 # 9

# servoreq = { # actuator movement request
#   "netSvcType" : 2, # transducer access services
#   "setSvcId" : 7, # write to channel of TIM
#   "msgType" : 1, # command
#   "msgLength" : 77, # bytes
#   "appId" : appId,
#   "ncapId" : servoId,
#   "timId" : rpiId,
#   "channelId" : 1,
#   "samplingMode" : 5, # continuous
#   "dataValue" : 0,
#   "timeout" : 60,
# }

servoreq = bytearray(81)
servoreq[0] = 2 # netSvcType
servoreq[1] = 7 # netSvcId
servoreq[2] = 1 # msgType
servoreq[3] = 77 # msgLength
servoreq[4] = 0x04 # UUID appId 0
servoreq[5] = 0x10 # 1
servoreq[6] = 0x00 # 2
servoreq[7] = 0x00 # 3
servoreq[8] = 0x27 # 4
servoreq[9] = 0x00 # 5
servoreq[10] = 0x00 # 6
servoreq[11] = 0x4D # 7
servoreq[12] = 0x00 # 8
servoreq[13] = 0x00 # 9
servoreq[14] = 0x00 # 10
servoreq[15] = 0x07 # 11
servoreq[16] = 0xE9 # 12
servoreq[17] = 0x00 # 13
servoreq[18] = 0x00 # 14
servoreq[19] = 0x00 # 15
servoreq[20] = 0x04 # UUID ncapId 0
servoreq[21] = 0x10 # 1
servoreq[22] = 0x00 # 2
servoreq[23] = 0x00 # 3
servoreq[24] = 0x27 # 4
servoreq[25] = 0x00 # 5
servoreq[26] = 0x00 # 6
servoreq[27] = 0x4D # 7
servoreq[28] = 0x00 # 8
servoreq[29] = 0x00 # 9
servoreq[30] = 0x03 # 10
servoreq[31] = 0x07 # 11
servoreq[32] = 0xE9 # 12
servoreq[33] = 0x00 # 13
servoreq[34] = 0x00 # 14
servoreq[35] = 0x00 # 15
servoreq[36] = 0x04 # UUID timId 0
servoreq[37] = 0x10 # 1
servoreq[38] = 0x00 # 2
servoreq[39] = 0x00 # 3
servoreq[40] = 0x27 # 4
servoreq[41] = 0x00 # 5
servoreq[42] = 0x00 # 6
servoreq[43] = 0x4D # 7
servoreq[44] = 0x00 # 8
servoreq[45] = 0x00 # 9
servoreq[46] = 0x01 # 10
servoreq[47] = 0x07 # 11
servoreq[48] = 0xE9 # 12
servoreq[49] = 0x00 # 13
servoreq[50] = 0x00 # 14
servoreq[51] = 0x00 # 15
servoreq[52] = 1 # channelId 0
servoreq[53] = 0 # 1
servoreq[54] = 5 # samplingMode 0
servoreq[55] = 0 # dataValue 0
servoreq[56] = 0 # 1
servoreq[57] = 0 # 2
servoreq[58] = 0 # 3
servoreq[59] = 0 # 4
servoreq[60] = 0 # 5
servoreq[61] = 0 # 6
servoreq[62] = 0 # 7
servoreq[63] = 0 # 8
servoreq[64] = 0 # 9
servoreq[65] = 0 # 10
servoreq[66] = 0 # 11
servoreq[67] = 0 # 12
servoreq[68] = 0 # 13
servoreq[69] = 0 # 14
servoreq[70] = 0 # 15
servoreq[71] = 0x00 # timeout 0
servoreq[72] = 0x3C # 1
servoreq[73] = 0 # 2
servoreq[74] = 0 # 3
servoreq[75] = 0 # 4
servoreq[76] = 0 # 5
servoreq[77] = 0 # 6
servoreq[78] = 0 # 7
servoreq[79] = 0 # 8
servoreq[80] = 0 # 9

# def hexstr_to_bytes(hexstr):
#     return bytes.fromhex(hexstr)

# def build_request_binary(req_dict):
#     return struct.pack(
#         "!BBBH16s16s16sBBH",
#         req_dict["netSvcType"],
#         req_dict["netSvcId"],
#         req_dict["msgType"],
#         req_dict["msgLength"],
#         hexstr_to_bytes(req_dict["appId"]),
#         hexstr_to_bytes(req_dict["ncapId"]),
#         hexstr_to_bytes(req_dict["timId"]),
#         req_dict["channelId"],
#         req_dict["samplingMode"],
#         req_dict["timeout"]
#     )

# def parse_response_binary(payload):
#     header_format = "!BBBH16s16s16sBBH"
#     header_size = struct.calcsize(header_format)
#     parts = struct.unpack(header_format, payload[:header_size])
#     temp_value = struct.unpack("!f", payload[header_size:header_size+4])[0]
#     response = {
#         "netSvcType": parts[0],
#         "netSvcId": parts[1],
#         "msgType": parts[2],
#         "msgLength": parts[3],
#         "appId": parts[4].hex(),
#         "ncapId": parts[5].hex(),
#         "timId": parts[6].hex(),
#         "channelId": parts[7],
#         "samplingMode": parts[8],
#         "timeout": parts[9],
#         "transducerSampleData": temp_value
#     }
#     return response

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
  client.publish("_1451.1.6/D0/SMARTSENSOR", sensorreq)
  print(f">Published request '{sensorreq}' to topic '_1451.1.6/D0/SMARTSENSOR'")
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
  payload = msg.payload
  curr_time = round(time.time() - start_time, 3)
  if (payload[2] == 2): # response
    print(">Received sensor read response on topic " + msg.topic)
  
    if (payload[22:38] == bytes([0x04, 0x10, 0x00, 0x00, 0x27, 0x00, 0x00, 0x4D, 0x00, 0x00, 0x02, 0x07, 0xE9, 0x00, 0x00, 0x00])): # sensorId check
      temp_bytes = payload[56:60]
      curr_temp = struct.unpack(">f", temp_bytes)[0]  # now a float
      temp_values.append(curr_temp)
      time_values.append(curr_time)

      text_box.config(state='normal')
      text_box.insert(tk.END, f"{curr_time:.3f}s: Smart sensor data received: {curr_temp:.3f} C")
      
      if curr_temp >= 27.0:
        client.publish("_1451.1.6/D0/SMARTACTUATOR", servoreq)
        print(f">Published request '{servoreq}' to topic '_1451.1.6/D0/SMARTACTUATOR'")  
        text_box.insert(tk.END, " --> Smart actuator write request published.")
      text_box.insert(tk.END, "\n")
      text_box.config(state='disabled')

      update_plot() # update graph
    
    elif (payload[22:37] == bytes([0x04, 0x10, 0x00, 0x00, 0x27, 0x00, 0x00, 0x4D, 0x00, 0x00, 0x03, 0x07, 0xE9, 0x00, 0x00, 0x00])): # servoId check
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
