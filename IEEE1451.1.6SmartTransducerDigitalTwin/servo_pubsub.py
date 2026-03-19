#!/usr/bin/python
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO
import time

appId = "041000002700004D00000007E90000000000"
rpiId = "041000002700004D00000107E90000000000"
servoId = "041000002700004D00000307E90000000000"

servorep = { # actuator movement reply (confirmation)
  "netSvcType" : 2, # transducer access services
  "netSvcId" : 7, # write to channel of TIM
  "msgType" : 2, # reply
  "msgLength" : 61, # bytes
  "errorCode" : 0,
  "appId" : appId,
  "ncapId" : servoId,
  "timId" : rpiId,
  "channelId" : 1,
  "transducerSampleData" : "0",
  "timestamp" : None
}
 
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
  payload = json.loads(msg.payload)
  if payload["msgType"] == 1: # request
    print(">Received request '" + str(payload) + "' on topic '" + msg.topic)

    if bytes.fromhex(payload["ncapId"]) == bytes.fromhex(servoId): # compare as 16-byte values
      setAngle(90)
      setAngle(0)

      t = time.time() # timestamp, convert from bytes to hex for JSON packable format
      sec = int(t)
      nsec = int((t - sec) * 1_000_000_000)
      sec_bytes = sec.to_bytes(6, byteorder='big')
      nsec_bytes = nsec.to_bytes(4, byteorder='big')
      timestamp_bytes = sec_bytes + nsec_bytes
      servorep["timestamp"] = timestamp_bytes.hex()

      client.publish("_1451.1.6/D0/SMARTACTUATOR", json.dumps(servorep))
      print(f">Published response '{json.dumps(servorep)}' to topic '_1451.1.6/D0/SMARTACTUATOR'")


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
