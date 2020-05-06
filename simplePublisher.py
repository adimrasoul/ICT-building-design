import paho.mqtt.client as PahoMQTT
import time
import pandas as pd
import json

class MyPublisher:
	def __init__(self, clientID):
		self.clientID = clientID
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self.messageBroker = 'localhost'

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, message, 2)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))



if __name__ == "__main__":
	test = MyPublisher("MyPublisher")
	test.start()
	df_columns = ['Date_Time', 't_in', 't_out', 'total_power']
	df = pd.read_csv('/home/ict4bd/Desktop/Project/simulation_Data_3Year.csv', sep=',', usecols=df_columns, index_col=0)
	df.index = pd.to_datetime(df.index, format='%Y/%m/%d  %H:%M:%S')
	GATEWAY_NAME = "VirtualBuilding"
	for i in df.index:
		for j in df.loc[i].items():
			key = j[0]
			value = j[1]
			if key == 'total_power':
				measurement = "Power"
			else:
				measurement = "Temperature"
			payload = {
						"location": str(GATEWAY_NAME),
						"measurement": measurement,
						"node": str(key),
						"time_stamp": str(i),
						"value": value}
			test.myPublish('ict4bd', json.dumps(payload))
			time.sleep(0.1)
	test.stop()


