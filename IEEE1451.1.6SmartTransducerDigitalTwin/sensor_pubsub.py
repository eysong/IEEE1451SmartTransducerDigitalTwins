#!/usr/bin/python
## import LCD1602
import os
import glob
import paho.mqtt.client as mqtt
import json
import time

def read_temp():
  f = open(glob.glob('/sys/bus/w1/devices/28*')[0] + '/w1_slave', 'r')
  lines = f.readlines()
  f.close()
  if lines[0].strip()[-3:] != 'YES':
    return None
  equals_pos = lines[1].find('t=')
  if equals_pos != -1:
    temp_string = lines[1][equals_pos + 2:]
    temp_c = float(temp_string)/1000.000
    return temp_c
  return None

appId = "041000002700004D00000007E90000000000"
rpiId = "041000002700004D00000107E90000000000"
sensorId = "041000002700004D00000207E90000000000"

sensorrep = { # sensor read reply (data)
  "netSvcType" : 2, # trasducer access services
  "netSvcId" : 1, # read from channel of TIM
  "msgType" : 2, # reply
  "msgLength" : 61, # bytes
  "errorCode" : 0,
  "appId" : appId,
  "ncapId" : sensorId,
  "timId" : rpiId,
  "channelId" : 1,
  "transducerSampleData" : str(read_temp()),
  "timestamp" : None
}
 
# when connected with broker
def on_connect(client, userdata, flag, rc):
  print(">Connected with result code " + str(rc))
  client.subscribe("_1451.1.6/D0/SMARTSENSOR")

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
  if payload["msgType"] == 1: # request
    print(">Received request '" + str(payload) + "' on topic " + msg.topic)
    
    if bytes.fromhex(payload["ncapId"]) == bytes.fromhex(sensorId): # compare as 16-byte values
      temp_c = read_temp()
      ## LCD1602.clear()
      ## LCD1602.write(0, 0, f'Temp: {temp_c: .3f} C')
      ## LCD1602.write(0, 1, f'      {temp_c * (9/5) + 32: .3f} F')
      
      sensorrep["transducerSampleData"] = temp_c

      t = time.time() # timestamp, convert from bytes to hex for JSON packable format
      sec = int(t)
      nsec = int((t - sec) * 1_000_000_000)
      sec_bytes = sec.to_bytes(6, byteorder='big')
      nsec_bytes = nsec.to_bytes(4, byteorder='big')
      timestamp_bytes = sec_bytes + nsec_bytes
      sensorrep["timestamp"] = timestamp_bytes.hex()

      client.publish("_1451.1.6/D0/SMARTSENSOR" , json.dumps(sensorrep))
      print(f">Published response '{json.dumps(sensorrep)}' to topic '_1451.1.6/D0/SMARTSENSOR'")
      sensorrep["transducerSampleData"] = None

  

## LCD1602.init(0x27, 1)  
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
  
client.connect("192.168.1.33", 1883, 60)
client.loop_forever()
