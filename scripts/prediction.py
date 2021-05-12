#!/usr/bin/env python
import rospy
from std_msgs.msg import Bool, Time
from geometry_msgs.msg import Vector3Stamped

import os
import scandir
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression

models = {}
pixels = np.array([])
pub = None
count = 0

def callback(msg):
	global pub, models, count, pixels

	count += 1
	if count == 1:
		pixels = np.append(pixels, np.array([msg.vector.x, msg.vector.y]))
		pixels = pixels.reshape(1, -1)
	else:
		pixels = np.append(pixels, np.array([msg.vector.x, msg.vector.y]).reshape(1, -1), axis=0)

	if pixels.size == 8: # {3 pixels : 6, 4 pixels : 8, 5 pixels: 10, 6 pixels : 12}
		print(msg.vector.x, msg.vector.y)
		# print(pixels)
		# rospy.loginfo('Third pixel available at {} secs'.format(rospy.Time.now()))
		clf = pickle.load(open(models[count], 'rb'))
		pixels_reshaped = pixels.reshape(1, -1)
		prediction = clf.predict(pixels_reshaped)
		pred_msg = Bool()
		pred_msg.data = True if prediction == 'R' else False
		rospy.loginfo('Predicted {} '.format(prediction))
		pub.publish(pred_msg)
		prediction_time = Time()
		prediction_time.data = rospy.Time.now()
		prediction_time_pub.publish(prediction_time)
		

if __name__ == "__main__":
	rospy.init_node('prediction')

	os.chdir('/home/ttsitos/object_reaching/learning/models/logistic_regression/protocol_2/H1_O1')
	model_names = [i.name for i in scandir.scandir('.')]
	model_names = sorted(model_names)

	for i in range(1, 11):
		models.update({i : model_names[i-1]})

	sub = rospy.Subscriber('/filtered_pixels', Vector3Stamped, callback)
	pub = rospy.Publisher('/prediction', Bool, queue_size=10)
	prediction_time_pub = rospy.Publisher('/prediction_time_topic', Time, queue_size=10)
	
	rospy.sleep(0.1)
	rospy.loginfo("Ready to accept pixels")
	rospy.spin()
