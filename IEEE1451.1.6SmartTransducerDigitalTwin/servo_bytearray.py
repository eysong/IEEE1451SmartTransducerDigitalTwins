#!/usr/bin/python
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# appId = "041000002700004D00000007E90000000000"
# rpiId = "041000002700004D00000107E90000000000"
# servoId = "041000002700004D00000307E90000000000"

# servorep = { # actuator movement reply(confirmation)
#   "netSvcType": 2, # transducer access services
#   "netSvcId": 7, # write to channel of TIM
#   "msgType": 2, # reply
#   "msgLength": 52, # bytes
#   "errorCode": 0,
#   "appId": appId,
#   "ncapId": servoId,
#   "timId": rpiId,
#   "channelId": 1,
# }

servorep = bytearray(56)
servorep[0] = 2 # netSvcType
servorep[1] = 7 # netSvcId
servorep[2] = 2 # msgType
servorep[3] = 52 # msgLength
servorep[4] = 0 # errorCode 0
servorep[5] = 0 # 1
servorep[6]  = 0x04 # UUID appId 0
servorep[7]  = 0x10 # 1
servorep[8]  = 0x00 # 2
servorep[9]  = 0x00 # 3
servorep[10] = 0x27 # 4
servorep[11] = 0x00 # 5
servorep[12] = 0x00 # 6
servorep[13] = 0x4D # 7
servorep[14] = 0x00 # 8
servorep[15] = 0x00 # 9
servorep[16] = 0x00 # 10
servorep[17] = 0x07 # 11
servorep[18] = 0xE9 # 12
servorep[19] = 0x00 # 13
servorep[20] = 0x00 # 14
servorep[21] = 0x00 # 15
servorep[22] = 0x04 # UUID ncapId 0
servorep[23] = 0x10 # 1
servorep[24] = 0x00 # 2
servorep[25] = 0x00 # 3
servorep[26] = 0x27 # 4
servorep[27] = 0x00 # 5
servorep[28] = 0x00 # 6
servorep[29] = 0x4D # 7
servorep[30] = 0x00 # 8
servorep[31] = 0x00 # 9
servorep[32] = 0x03 # 10
servorep[33] = 0x07 # 11
servorep[34] = 0xE9 # 12
servorep[35] = 0x00 # 13
servorep[36] = 0x00 # 14
servorep[37] = 0x00 # 15
servorep[38] = 0x04 # UUID timId 0
servorep[39] = 0x10 # 1
servorep[40] = 0x00 # 2
servorep[41] = 0x00 # 3
servorep[42] = 0x27 # 4
servorep[43] = 0x00 # 5
servorep[44] = 0x00 # 6
servorep[45] = 0x4D # 7
servorep[46] = 0x00 # 8
servorep[47] = 0x00 # 9
servorep[48] = 0x01 # 10
servorep[49] = 0x07 # 11
servorep[50] = 0xE9 # 12
servorep[51] = 0x00 # 13
servorep[52] = 0x00 # 14
servorep[53] = 0x00 # 15
servorep[54] = 1 # channelId 0
servorep[55] = 0 # 1

# when connected with broker
def on_connect(client, userdata, flag, rc):
  print(">Connected with result code " + str(rc))
  client.subscribe("_1451.1.6/D0/SMARTACTUATOR")

# when disconnected with broker
def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print(">Unexpected disconnection.")

# when received messages
def on_message(client, userdata, msg):
  payload = msg.payload
  if payload[2] == 1: # request
    print(">Received write request on topic '" + msg.topic)

    if (payload[20:36] == bytes([0x04, 0x10, 0x00, 0x00, 0x27, 0x00, 0x00, 0x4D, 0x00, 0x00, 0x03, 0x07, 0xE9, 0x00, 0x00, 0x00])): # servoId check
      setAngle(90)
      setAngle(0)

      client.publish("_1451.1.6/D0/SMARTACTUATOR", servorep)
      print(f">Published response '{servorep}' to topic '_1451.1.6/D0/SMARTACTUATOR'")


# servo setup    
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

def setAngle(angle):
  duty = angle / 18 + 2
  GPIO.output(18, True)
  pwm.ChangeDutyCycle(duty)
  time.sleep(1)
  GPIO.output(18, False)
  pwm.ChangeDutyCycle(0)

client = mqtt.Client() 
client.on_connect = on_connect   
client.on_disconnect = on_disconnect
client.on_message = on_message
 
client.connect("192.168.1.33", 1883, 60)
client.loop_forever()
pwm.stop()
GPIO.cleanup()
