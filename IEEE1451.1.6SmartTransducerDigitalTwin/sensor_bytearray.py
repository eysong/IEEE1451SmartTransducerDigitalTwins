#!/usr/bin/python
## import LCD1602
import os
import glob
import paho.mqtt.client as mqtt
import time
import struct

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

# appId = "041000002700004D00000007E90000000000"
# rpiId = "041000002700004D00000107E90000000000"
# sensorId = "041000002700004D00000207E90000000000"

# sensorrep = { # sensor read reply (data)
#   "netSvcType" : 2, # trasducer access services
#   "netSvcId" : 1, # read from channel of TIM
#   "msgType" : 2, # reply
#   "msgLength" : 78, # bytes
#   "errorCode" : 0,
#   "appId" : appId,
#   "ncapId" : sensorId,
#   "timId" : rpiId,
#   "channelId" : 1,
#   "transducerSampleData" : str(read_temp()),
#   "timestamp" : None
# } 

sensorrep = bytearray(82)
sensorrep[0] = 2 # netSvcType
sensorrep[1] = 1 # netSvcId
sensorrep[2] = 2 # msgType
sensorrep[3] = 78 # msgLength
sensorrep[4] = 0 # errorCode 0
sensorrep[5] = 0 # 1
sensorrep[6]  = 0x04 # UUID appId 0
sensorrep[7]  = 0x10 # 1
sensorrep[8]  = 0x00 # 2
sensorrep[9]  = 0x00 # 3
sensorrep[10] = 0x27 # 4
sensorrep[11] = 0x00 # 5
sensorrep[12] = 0x00 # 6
sensorrep[13] = 0x4D # 7
sensorrep[14] = 0x00 # 8
sensorrep[15] = 0x00 # 9
sensorrep[16] = 0x00 # 10
sensorrep[17] = 0x07 # 11
sensorrep[18] = 0xE9 # 12
sensorrep[19] = 0x00 # 13
sensorrep[20] = 0x00 # 14
sensorrep[21] = 0x00 # 15
sensorrep[22] = 0x04 # UUID ncapId 0
sensorrep[23] = 0x10 # 1
sensorrep[24] = 0x00 # 2
sensorrep[25] = 0x00 # 3
sensorrep[26] = 0x27 # 4
sensorrep[27] = 0x00 # 5
sensorrep[28] = 0x00 # 6
sensorrep[29] = 0x4D # 7
sensorrep[30] = 0x00 # 8
sensorrep[31] = 0x00 # 9
sensorrep[32] = 0x02 # 10
sensorrep[33] = 0x07 # 11
sensorrep[34] = 0xE9 # 12
sensorrep[35] = 0x00 # 13
sensorrep[36] = 0x00 # 14
sensorrep[37] = 0x00 # 15
sensorrep[38] = 0x04 # UUID timId 0
sensorrep[39] = 0x10 # 1
sensorrep[40] = 0x00 # 2
sensorrep[41] = 0x00 # 3
sensorrep[42] = 0x27 # 4
sensorrep[43] = 0x00 # 5
sensorrep[44] = 0x00 # 6
sensorrep[45] = 0x4D # 7
sensorrep[46] = 0x00 # 8
sensorrep[47] = 0x00 # 9
sensorrep[48] = 0x01 # 10
sensorrep[49] = 0x07 # 11
sensorrep[50] = 0xE9 # 12
sensorrep[51] = 0x00 # 13
sensorrep[52] = 0x00 # 14
sensorrep[53] = 0x00 # 15
sensorrep[54] = 1 # channelId 0
sensorrep[55] = 0 # 1
sensorrep[56] = 0 # transducerSampleData 0
sensorrep[57] = 0 # 1
sensorrep[58] = 0 # 2
sensorrep[59] = 0 # 3
sensorrep[60] = 0 # 4
sensorrep[61] = 0 # 5
sensorrep[62] = 0 # 6
sensorrep[63] = 0 # 7
sensorrep[64] = 0 # 8
sensorrep[65] = 0 # 9
sensorrep[66] = 0 # 10
sensorrep[67] = 0 # 11
sensorrep[68] = 0 # 12
sensorrep[69] = 0 # 13
sensorrep[70] = 0 # 14
sensorrep[71] = 0 # 15
sensorrep[72] = 0 # timestamp 0
sensorrep[73] = 0 # 1
sensorrep[74] = 0 # 2
sensorrep[75] = 0 # 3
sensorrep[76] = 0 # 4
sensorrep[77] = 0 # 5
sensorrep[78] = 0 # 6
sensorrep[79] = 0 # 7
sensorrep[80] = 0 # 8
sensorrep[81] = 0 # 9

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
  payload = msg.payload 
  
  if payload[2] == 1: # request
    print(">Received sensor read request on topic " + msg.topic)
    if (payload[20:36] == bytes([0x04, 0x10, 0x00, 0x00, 0x27, 0x00, 0x00, 0x4D, 0x00, 0x00, 0x02, 0x07, 0xE9, 0x00, 0x00, 0x00])): # sensorId check
      temp_c = read_temp()
      ## LCD1602.clear()
      ## LCD1602.write(0, 0, f'Temp: {temp_c: .3f} C')
      ## LCD1602.write(0, 1, f'      {temp_c * (9/5) + 32: .3f} F')
      
      temp_bytes = bytearray(struct.pack(">f", temp_c))  # Big-endian float
      sensorrep[56:60] = temp_bytes

      t = time.time() # timestamp
      sec = int(t)
      nsec = int((t - sec) * 1_000_000_000)
      sec_bytes = sec.to_bytes(6, byteorder='big')
      nsec_bytes = nsec.to_bytes(4, byteorder='big')
      timestamp_bytes = sec_bytes + nsec_bytes
      sensorrep[72:82] = timestamp_bytes

      client.publish("_1451.1.6/D0/SMARTSENSOR" , sensorrep)
      print(f">Published read response to topic '_1451.1.6/D0/SMARTSENSOR'")

      for i in range(56, 72):  # clear transducerSampleData
        sensorrep[i] = 0

  

## LCD1602.init(0x27, 1)  
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
  
client.connect("192.168.1.33", 1883, 60)
client.loop_forever()
