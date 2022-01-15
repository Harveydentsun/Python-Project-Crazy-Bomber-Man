
import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense
import tensorflow as tf

input_shape =(11,13,11)
input = tf.Variable(tf.ones([1,11,13,11]))

layer1 = Conv2D(64, 4, strides=(2, 2),
                      padding='valid',
                      activation='relu',
                      input_shape=input_shape,
                      data_format='channels_last')
y1=layer1(input)
layer2 = Conv2D(32, 2, strides=(1, 1),
                      padding='valid',
                      activation='relu',
                      input_shape=input_shape,
                      data_format='channels_last')
y2=layer2(y1)






model = Sequential()

# First convolutional layer
model.add(Conv2D(64, 4, strides=(2, 2),
                      padding='valid',
                      activation='relu',
                      input_shape=input_shape,
                      data_format='channels_last'))

# Second convolutional layer
model.add(Conv2D(32, 2, strides=(1, 1),
                      padding='valid',
                      activation='relu',
                      input_shape=input_shape,
                      data_format='channels_last'))


# Flatten the convolution output
model.add(Flatten())

# First dense layer
model.add(Dense(512, activation='relu'))

# Output layer
model.add(Dense(6))

model.compile(loss='mean_squared_error',
                           optimizer='rmsprop',
                           metrics=['accuracy'])