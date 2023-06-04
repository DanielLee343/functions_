import tensorflow as tf
from tensorflow.keras.datasets import cifar100
from tensorflow.keras.applications.mobilenet import MobileNet
import time, sys
import numpy as np
import os, subprocess

num_iter = int(sys.argv[1])
run_damo = bool(sys.argv[2])
# Load CIFAR-100 dataset
(x_train, y_train), (x_test, y_test) = cifar100.load_data()

# Preprocess the data
x_test = tf.keras.applications.mobilenet.preprocess_input(x_test)
duplicated_data = np.repeat(x_test, num_iter, axis=0)

# Load the MobileNet model (without the top layer)
base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(32, 32, 3))

# Freeze the base model's weights
base_model.trainable = False

# Add a global average pooling layer
global_avg_pooling = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)

# Add a dense output layer with 100 units (for CIFAR-100 classes)
output = tf.keras.layers.Dense(100, activation='softmax')(global_avg_pooling)

# Create the model
model = tf.keras.Model(inputs=base_model.input, outputs=output)

# Load pre-trained weights (if available)
# model.load_weights('mobilenet_cifar100.h5')

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Perform inference on the test data
# print("running interference {} time".format(num_iter))
start = time.time()
if run_damo:
    check_pid = str(os.getpid())
    directory_path = "/home/cc/functions/run_bench/playground/dl_inference"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    damo_trace = os.path.join(directory_path, "dl_inference.data")
    print("damo_trace file is: ", damo_trace)
    # time.sleep(5)
    subprocess.Popen(["sudo","damo","record", "-s", "1000", "-a", "100000", "-u",
                        "1000000", "-n", "5000", "-m", "6000", "-o", 
                    damo_trace, check_pid])
predictions = model.predict(duplicated_data)
end = time.time()
print("inference time: {:.2f}".format(end - start))

# Get the predicted class labels
predicted_labels = tf.argmax(predictions, axis=1)

# Print some example predictions
# for i in range(10):
#     print('Predicted class:', predicted_labels[i])
