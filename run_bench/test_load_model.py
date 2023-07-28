import tensorflow as tf
import os

model = tf.keras.applications.resnet50.ResNet50()

# ... Perform operations with the model ...

# Save the model to a specific location
model_path = './resnet50_test'
# model.save(model_path)
model = tf.keras.models.load_model(model_path)