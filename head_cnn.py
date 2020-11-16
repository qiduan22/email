"""
============================
Gradient Boosting regression
============================

Demonstrate Gradient Boosting on the Boston housing dataset.

This example fits a Gradient Boosting model with least squares loss and
500 regression trees of depth 4.
"""
print(__doc__)

# Author: Peter Prettenhofer <peter.prettenhofer@gmail.com>
#
# License: BSD 3 clause

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

from sklearn import ensemble
from sklearn import datasets
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from enum import IntEnum
from collections import defaultdict

#import BasicRatios.ratios_enum as ratios_enum

#import tensorflow as tf
import math
import nltk

#import ClassifierCNN.cls_cnn_enum as cls_cnn_enum
import inspect, os

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

learning_rate = 0.001
epoches_total = 5000
mini_batch_size    = 10
y_range_start = 110
y_range_end = 180
range_number_of_divisions = 7
boolean_use_standardized_variables = 1
range_division_overlap = 2
TRAIN_TOTAL = 12800
DATA_TOTAL = 16000


class MyClassifierCnnFlags:
    def __init__(self):
        self.use_basic_ratios_info = True
        self.use_basic_ratios_info_log = True
        self.use_salsig_prob = True
        self.use_salsig_tfidf = True
        self.use_tfidf_prob = True
        self.use_tfidf_tfidf = True




class MyClassifierCnnTestAuthorData:
    def __init__(self):
        self.vector_basic_ratios_info = []
        self.vector_basic_ratios_info_log = []
        # self.vector_salsig_prob = []
        # self.vector_salsig_tfidf = []
        # self.vector_tfidf_prob = []
        # self.vector_tfidf_tfidf = []
        self.flags = MyClassifierCnnFlags()


class MyClassifierCnnTestResultElement:
    def __init__(self):
        self.author = 0
        self.others = 0
        self.raw_output = []

#class MyClassifierCnnTestResult:
#    def __init__(self):
#        self.author_name
#        self.elements = []

class MyClassifierCnnTestResult:
    def __init__(self):
        self.author_name = ""
        self.elements = []
        self.all_raw_outputs = []
        self.author_confidence = 0
        self.others_confidence = 0

class MyClassifierDecisionResult:
    def __init__(self):
        self.decision_author = MyClassifierCnnTestResult()
        self.all_results = []
        self.decision_author_confidence = 0
        self.total_author_confidence = 0




def train_cnn_network(author_name, in_xs_train, in_ys_train, in_xs_test, in_ys_test, save_to_file, use_previously_trained_file = False):
	#data are assumed to preprocessed already and ready to use in training
	in_xs_train = np.array(in_xs_train)
	in_ys_train = np.array(in_ys_train)
	in_xs_test = np.array(in_xs_test)
	in_ys_test = np.array(in_ys_test)
	print("author_name = ", author_name)
	print("in_xs.shape = ", in_xs_train.shape)
	print("in_ys.shape = ", in_ys_train.shape)
	use_previous_file = False
	if(use_previously_trained_file and os.path.exists(save_to_file)):
		use_previous_file = True

	#X_train, X_test, y_train, y_test = train_test_split(in_xs, in_ys, test_size=0.2, random_state=0)
	X_train = in_xs_train
	X_test = in_xs_test
	y_train = in_ys_train
	y_test = in_ys_test
	num_features = in_xs_train.shape[1]
	output_size = in_ys_train.shape[1]
	xs = tf.placeholder(tf.float32, [None, 1, num_features, 1])
	yt = tf.placeholder(tf.float32, [None, output_size])

	should_drop = tf.placeholder(tf.bool)

	# 5
	conv1 = tf.layers.conv2d(inputs=xs, filters=16, kernel_size=[1, num_features], padding="same", activation=tf.nn.relu)
	pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[1, 2], strides=2)
	conv2 = tf.layers.conv2d(inputs=pool1, filters=32, kernel_size=[5, (int)(num_features/4)], padding="same", activation=tf.nn.relu)
	pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[1, 2], strides=2)
	pool_flat = tf.reshape(pool2, [-1, int(int(num_features / 2) / 2) * 32])
	hidden = tf.layers.dense(inputs=pool_flat, units=100, activation=tf.nn.sigmoid)
	dropout = tf.layers.dropout(inputs=hidden, rate=0.2, training=should_drop)
	output = tf.layers.dense(inputs=dropout, units=output_size)

	cost = tf.reduce_mean(tf.square(output - yt))
	#cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=yt, logits=output))

	train = tf.train.AdamOptimizer(2e-5).minimize(cost)

	init = tf.global_variables_initializer()
	saver = tf.train.Saver()
	print ("range = ", range(0, X_train.shape[0], mini_batch_size))

	with tf.Session() as sess:
		#saver.restore(sess, save_to_file)
		if(use_previous_file):
			saver.restore(sess, save_to_file)
		else:
			sess.run(init)

		print("===========" + author_name + "============")
		print("===========" + author_name + "============")
		print("===========" + author_name + "============")
		# Train
		for index in range(epoches_total):
			#break
			X_train, y_train = shuffle(X_train, y_train)
			for i in range(0, X_train.shape[0], mini_batch_size):
				# print("i = ", i)
				mini_end = i + mini_batch_size
				if (mini_end > X_train.shape[0]):
					mini_end = X_train.shape[0]
				x_train_mini = X_train[i:mini_end]
				y_train_mini = y_train[i:mini_end]
				# print("x_train_mini = ", x_train_mini)
				sess.run([cost, train, output], feed_dict={xs: x_train_mini.reshape([-1, 1, X_train.shape[1], 1]),
														   yt: y_train_mini.reshape([-1, y_train.shape[1]]),
														   should_drop: True})  # print(sess.run([cost, train, output], feed_dict={xs: x_train_mini, yt: y_train_mini.reshape([-1, 1])}))
			if (index % 100 == 0):
				print("index = ", index)
				print(sess.run([cost], feed_dict={xs: X_train.reshape([-1, 1, X_train.shape[1], 1]),
												  yt: y_train.reshape([-1, y_train.shape[1]]), should_drop: False}))
			if (index % 300 == 0):
				saver.save(sess, save_to_file)

		# Test trained model
		saver.save(sess, save_to_file)
		print("=== test results ===")
		print(sess.run([cost, output],
					   feed_dict={xs: X_test.reshape([-1, 1, X_train.shape[1], 1]), yt: y_test.reshape([-1, y_train.shape[1]]),
								  should_drop: False}))
		tc, to = sess.run([cost, output],
				 feed_dict={xs: X_test.reshape([-1, 1, X_train.shape[1], 1]), yt: y_test.reshape([-1, y_train.shape[1]]),
							should_drop: False})
		print("*** tc = ", tc)
		print("y_test = ", y_test)
		print("=== all data results ===")
		print("*** 1")

		rc, ro = sess.run([cost, output],
						  feed_dict={xs: X_train.reshape([-1, 1, X_train.shape[1], 1]), yt: y_train.reshape([-1, y_train.shape[1]]),
									 should_drop: False})
		print("*** 2")
		print(sess.run([cost, output],
					   feed_dict={xs: X_train.reshape([-1, 1, X_train.shape[1], 1]), yt: y_train.reshape([-1, y_train.shape[1]]),
								  should_drop: False}))
		print("*** 3")
		print("*** rc = ", rc)
		#print("in_ys = ", in_ys)
		print("tc = ",tc, " - rc = ", rc)
		return [tc, rc]


def test_cnn_network(author_name, x, cnn_file):

	if (not os.path.exists(cnn_file+".index")):
		return None

	tf.reset_default_graph()

	x = np.array(x)
	num_features = len(x)
	output_size = 2

	xs = tf.placeholder(tf.float32, [None, 1, num_features, 1])
	yt = tf.placeholder(tf.float32, [None, output_size])

	should_drop = tf.placeholder(tf.bool)

	# 5
	conv1 = tf.layers.conv2d(inputs=xs, filters=16, kernel_size=[1, num_features], padding="same",
							 activation=tf.nn.relu)
	pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[1, 2], strides=2)
	conv2 = tf.layers.conv2d(inputs=pool1, filters=32, kernel_size=[5, (int)(num_features / 4)], padding="same",
							 activation=tf.nn.relu)
	pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[1, 2], strides=2)
	pool_flat = tf.reshape(pool2, [-1, int(int(num_features / 2) / 2) * 32])
	hidden = tf.layers.dense(inputs=pool_flat, units=100, activation=tf.nn.sigmoid)
	dropout = tf.layers.dropout(inputs=hidden, rate=0.2, training=should_drop)
	output = tf.layers.dense(inputs=dropout, units=output_size)

	cost = tf.reduce_mean(tf.square(output - yt))
	#cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=yt, logits=output))
	train = tf.train.AdamOptimizer(2e-5).minimize(cost)

	init = tf.global_variables_initializer()
	saver = tf.train.Saver()

	with tf.Session() as sess:
		saver.restore(sess, cnn_file)

		print("=== estimate value in range ===")
		print(sess.run([output], feed_dict={xs: x.reshape([-1, 1, num_features, 1]),
											should_drop: False}))
		est_author_value = sess.run([output], feed_dict={xs: x.reshape([-1, 1, num_features, 1]),
														   should_drop: False})
		print("est_author_value = ", est_author_value)


		return est_author_value[0]



def test_cnn_run_main(author_name, author_data, cnn_file):

	#xs_org = test_generate_cnn_author_data(author_data, flags)

	#cnn_xs = test_generate_normalize_cnn_input_data(xs_org, False, None)

	cnn_xs = author_data
	all_outputs = []
	result = MyClassifierCnnTestResult()
	result.author_name = author_name
	cnn_xs = np.array(cnn_xs)
	benign_count = 0
	ratio = []

	for i in range(cnn_xs.shape[0]):
		print("cnn_file = ", cnn_file)
		output_org_format = test_cnn_network(author_name, cnn_xs[i,:], cnn_file)
		output = output_org_format[0,:]
		print("output",output)
		elm = MyClassifierCnnTestResultElement()
		elm.author = math.exp(output[0])/(math.exp(output[0])+math.exp(output[1]))
		elm.others = math.exp(output[1])/(math.exp(output[0])+math.exp(output[1]))
		ratio.append([output[0], output[1]])
		if (output[0] < output[1]):
			benign_count = benign_count + 1
		elm.raw_output = output
		all_outputs.append(output)
		result.elements.append(elm)
	result.author_confidence = 0
	result.others_confidence = 0
	for i in range (cnn_xs.shape[0]):
		result.author_confidence = result.author_confidence +  result.elements[i].author
		result.others_confidence = result.others_confidence +  result.elements[i].others

	result.author_confidence = result.author_confidence/cnn_xs.shape[0]
	result.others_confidence = result.others_confidence/cnn_xs.shape[0]
	result.all_raw_outputs = all_outputs

	#print(result.elements)
	print('benign_count = ', benign_count)
	#return result
	return ratio


def hist(_data):
	total = len(_data)
	bin= [[0 for i in range(10)] for j in range(10)]
	for i in range(total):

		bin_loc0 = math.floor(_data[i][0] * 10)
		if (bin_loc0 >= 10):
			bin_loc0 = 9
		bin_loc1 = math.floor(_data[i][1] * 10)
		if (bin_loc1 >= 10):
			bin_loc1 = 9
		bin[bin_loc0][bin_loc1] += 1
	for i in range(len(bin)):
		for j in range(len(bin)):
			bin[i][j] = float(bin[i][j]/total)
	return bin

#all = np.loadtxt('all.txt')
b_all = np.loadtxt('b_all10.txt')
m_all = np.loadtxt('m_all10.txt')
train_data = []
for i in range(TRAIN_TOTAL):
	train_data_item = []
	for j in range(len(b_all[i])):
		train_data_item.append( int(b_all[i][j]) )
	train_data.append(train_data_item)

for i in range(TRAIN_TOTAL):
	train_data_item = []
	for j in range(len(m_all[i])):
		train_data_item.append( int(m_all[i][j]) )
	train_data.append(train_data_item)


#all_input = np.concatenate( (benign1, mali1), axis = 0 )

train_y = []
for i in range(TRAIN_TOTAL):
	train_y.append([0, 1])

for i in range(TRAIN_TOTAL):
	train_y.append([1, 0])

#benign2 = np.loadtxt('b2.txt')
#mali2 = np.loadtxt('m2.txt')
test_x = []
for i in range(TRAIN_TOTAL, DATA_TOTAL):
	test_x_item = []
	for j in range(len(b_all[i])):
		test_x_item.append( int(b_all[i][j]) )
	test_x.append(test_x_item)

test_x_mal = []
for i in range(TRAIN_TOTAL, DATA_TOTAL):
	test_x_mal_item = []
	for j in range(len(m_all[i])):
		test_x_mal_item.append( int(m_all[i][j]) )
	test_x_mal.append(test_x_mal_item)

test_y = []
for i in range(DATA_TOTAL - TRAIN_TOTAL):
	test_y.append([0, 1])

sender_test = []
for i in range(1024):
	#feature = []
	feature = [int(j) for j in bin(i)[2:].zfill(10)]
	sender_test.append(feature)
#print(all_input[0])


#train_cnn_network('all80', train_data, train_y, test_x, test_y, 'test10f',  False)




ratio = test_cnn_run_main('all_bit', sender_test, 'test10f')
for i in range(len(ratio)):
	if ratio[i][0] < 0:
		ratio[i][0] = 0
	if ratio[i][1] < 0:
		ratio[i][1] = 0
#print(ratio)
feature_dict = {}
for i in range(len(sender_test)):
	feature_dict[tuple(sender_test[i])] = ratio[i]
print(feature_dict)
benign_r = []
mal_r = []
for i in range(len(test_x)):
	benign_r.append(feature_dict[tuple(test_x[i])])
	mal_r.append(feature_dict[tuple(test_x_mal[i])])

benign_count = 0
benign_sus = 0
benign_fp = 0
for i in range(len(benign_r)):
	if benign_r[i][0] < 0.5 and benign_r[i][1] >= 0.5:
		benign_count += 1
	elif benign_r[i][0] >= 0.5 and benign_r[i][1] < 0.5:
		benign_fp += 1
	else:
		benign_sus += 1

mal_count = 0
mal_sus = 0
mal_fn = 0
for i in range(len(mal_r)):
	if mal_r[i][0] >= 0.5 and mal_r[i][1] < 0.5:
		mal_count += 1
	elif mal_r[i][0] < 0.5 and mal_r[i][1] >= 0.5:
		mal_fn += 1
	else:
		mal_sus += 1
print(benign_count, benign_sus, benign_fp)
print(mal_count, mal_sus, mal_fn)



