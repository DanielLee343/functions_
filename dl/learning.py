import resource, time
init_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
initTime = time.time()
print("MAKESPAN ::> Code deployed -> Time = {0}.s | Memory = {1}.MB".format(time.time()-initTime, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
import numpy as np # linear algebra
try:
    np.distutils.__config__.blas_opt_info = np.distutils.system_info.blas_opt_info
except Exception:
    print("cannot")
    pass
import os, sys, logging, json, shutil, pickle
# import lasagne
import tensorflow_datasets as tfds
import subprocess
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras import models
from tensorflow.keras.models import Model
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import callbacks
from tensorflow.keras.utils import get_file
from tensorflow.keras.preprocessing.image import img_to_array, array_to_img
import tensorflow as tf
import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("tensorflow").setLevel(logging.CRITICAL)
logging.getLogger("tensorflow_hub").setLevel(logging.CRITICAL)
CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
PROF_DIR_BASE= "/home/cc/functions/run_bench/vtune_log"
VTUNE = "/opt/intel/oneapi/vtune/2023.1.0/bin64/vtune"

class PrintLR(callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print("MAKESPAN ::> State {0} -> Time = {1}.s | Memory = {2}.MB".format(epoch, time.time()-initTime, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))

def run_train(params):
    # params = args.get('meta')
    # params = json.loads(params)
    print("---------------")
    dataset = params['dataset']
    selected_model = params['model']
    BATCH_SIZE = int(params['batch'])
    NB_EPOCHS = int(params['epochs'])
    features = params['features']
    label = int(features['class'])
    example = int(features['sample'])
    shape = features['shape']
    print(dataset)
    print(selected_model)
    print(BATCH_SIZE)
    print(NB_EPOCHS)
    print(shape)

    download_start = time.time()
    train_ds = tfds.load(name=dataset, split=tfds.Split.TRAIN, data_dir=CUR_DIR)
    train_ds = tfds.as_numpy(train_ds)
    train_X = np.asarray([im["image"] for im in train_ds])
    train_Y = np.asarray([im["label"] for im in train_ds])
    #train_X, train_Y = train_ds["image"], train_ds["label"]
    print("MAKESPAN ::> Data Loaded -> Time = {:.2f}.s | Memory = {}.MB".format(time.time()-download_start, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))

    classes = np.unique(train_Y)
    num_classes = len(classes)

    if shape[-1] < 3: #If is not RGB image
        train_X=np.dstack([train_X] * 3)
        # Reshape images as per the tensor format required by tensorflow
        train_X = train_X.reshape(-1, shape[0], shape[1], 3)

    # Resize the images 48*48 required by models for datasets having smaller sizes
    if shape[0] < 48:
         train_X = np.asarray([img_to_array(array_to_img(im, scale=False).resize((48,48))) for im in train_X])
    elif shape[0] > 56:
         train_X = np.asarray([img_to_array(array_to_img(im, scale=False).resize((56,56))) for im in train_X])

    # Normalise the data and change data type
    train_X = train_X / 255.
    train_X = train_X.astype('float32')
    # print("pre processing time:", time.time() - download_start)

    # Converting Labels to one hot encoded format
    train_label = to_categorical(train_Y)

    #  Create base model
    print(selected_model)
    if selected_model == 'vgg16':
        from tensorflow.keras.applications import vgg16
        train_X = vgg16.preprocess_input(train_X)
        conv_base = vgg16.VGG16(weights='imagenet',include_top=False,input_shape=(train_X.shape[1], train_X.shape[2], train_X.shape[3]))
    elif selected_model == 'resnet50':
        from tensorflow.keras.applications import ResNet50
        from tensorflow.keras.applications.resnet import preprocess_input
        train_X = preprocess_input(train_X)
        conv_base = ResNet50(input_shape=(train_X.shape[1], train_X.shape[2], train_X.shape[3]), include_top=False, weights='imagenet', pooling='max')
    elif selected_model == 'resnet152':
        from tensorflow.keras.applications import ResNet152
        from tensorflow.keras.applications.resnet import preprocess_input
        train_X = preprocess_input(train_X)
        conv_base = ResNet152(input_shape=(train_X.shape[1], train_X.shape[2], train_X.shape[3]), include_top=False, weights='imagenet', pooling='max')
    elif selected_model == 'mobilenet':
        from tensorflow.keras.applications import MobileNet
        from tensorflow.keras.applications.mobilenet import preprocess_input
        train_X = preprocess_input(train_X)
        conv_base = MobileNet(input_shape=(train_X.shape[1], train_X.shape[2], train_X.shape[3]), include_top=False, weights='imagenet', pooling='max')
    else:
        print('The requested model is currently not supported.')
        sys.exit(0)

    print("MAKESPAN ::> Data Processed -> Time = {0}.s | Memory = {1}.MB".format(time.time()-initTime, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
    train_features = conv_base.predict(np.array(train_X), batch_size=BATCH_SIZE, verbose=2)
    for layer in conv_base.layers:
        layer.trainable = False

    # Saving the features so that they can be used for future
    np.savez("train_features", train_features, train_label)
    print("MAKESPAN ::> Predict and Save -> Time = {0}.s | Memory = {1}.MB".format(time.time()-initTime, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))

    # Flatten extracted features
    train_features_flat = np.reshape(train_features, (train_features.shape[0], 1*1*train_features.shape[-1]))

    model = models.Sequential()
    model.add(layers.Dense(64, activation='relu', input_dim=(1*1*train_features.shape[-1])))
    model.add(layers.Dense(label, activation='softmax'))

    # Define the checkpoint directory to store the checkpoints
    checkpoint_dir = './training_checkpoints'
    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    callback = [
        callbacks.TensorBoard(log_dir='./logs'),
        callbacks.ModelCheckpoint(filepath=checkpoint_prefix,
                                           save_weights_only=True),
        PrintLR()
    ]

    # Compile the model.
    model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizers.Adam(),
        metrics=['acc'])

    print("MAKESPAN ::> Ready for Training -> Time = {0}.s | Memory = {1}.MB".format(time.time()-initTime, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
    history = model.fit(
        train_features_flat,
        train_label,
        epochs=NB_EPOCHS,
        callbacks=callback
    )
    final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 - init_memory
    print("MAKESPAN ::> Function completion -> Time = {0}.s | Memory = {1}.MB".format(time.time()-initTime, final_memory))
    output = {'Response': 'FUNCTION COMPLETED SUCCESSFULLY (*_*)'}
    return output

def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo)
    return dict

def load_imagenet(data_folder, idx, img_size=64):
    data_file = os.path.join(data_folder, 'train_data_batch_')

    d = unpickle(data_file + str(idx))
    x = d['data']
    y = d['labels']
    mean_image = d['mean']

    x = x/np.float32(255)
    mean_image = mean_image/np.float32(255)

    # Labels are indexed from 1, shift it so that indexes start at 0
    y = [i-1 for i in y]
    data_size = x.shape[0]

    x -= mean_image

    img_size2 = img_size * img_size

    x = np.dstack((x[:, :img_size2], x[:, img_size2:2*img_size2], x[:, 2*img_size2:]))
    x = x.reshape((x.shape[0], img_size, img_size, 3))

    # create mirrored images
    X_train = x[0:data_size, :, :, :]
    Y_train = y[0:data_size]
    X_train_flip = X_train[:, :, :, ::-1]
    Y_train_flip = Y_train
    X_train = np.concatenate((X_train, X_train_flip), axis=0)
    Y_train = np.concatenate((Y_train, Y_train_flip), axis=0)

    return dict(
        X_train = X_train.astype('float32'),
        # X_train=lasagne.utils.floatX(X_train),
        Y_train=Y_train.astype('int32'),
        mean=mean_image)

def run_transfer(params):
    print("---------------")
    dataset = params['dataset']
    selected_model = params['model']
    BATCH_SIZE = int(params['batch'])
    NB_EPOCHS = int(params['epochs'])
    # features = params['features']
    # label = int(features['class'])
    # example = int(features['sample'])
    # shape = features['shape']
    print(dataset)
    print(selected_model)
    print(BATCH_SIZE)
    print(NB_EPOCHS)
    print("---------------")

    start_preprocess = time.time()
    if os.path.isfile(dataset) == True:
        dataset = np.load(dataset)
        x_train = dataset['x_train']
        y_train = dataset['y_train']
        # x_test = dataset['x_test']
        # y_test = dataset['y_test']
    else:
        # (x_train, y_train), (x_test, y_test) = tfds.load(name=dataset, split=tfds.Split.TRAIN, data_dir=CUR_DIR)
        if dataset == "mnist":
            from tensorflow.keras.datasets import mnist
            (x_train, y_train), (x_test, y_test) = mnist.load_data()
            shape = [28, 28, 1]
            classes = 10
        elif dataset == "fashion_mnist":
            from tensorflow.keras.datasets import fashion_mnist
            (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
            shape = [28, 28, 1]
            classes = 10
        elif dataset == "cifar10":
            from tensorflow.keras.datasets import cifar10
            (x_train, y_train), (x_test, y_test) = cifar10.load_data()
            shape = [32, 32, 3]
            classes = 10
        elif dataset == "cifar100":
            from tensorflow.keras.datasets import cifar100
            (x_train, y_train), (x_test, y_test) = cifar100.load_data()
            shape = [32, 32, 3]
            classes = 100
        elif dataset == "downsample_imagenet":
            loaded_data = load_imagenet(CUR_DIR, 1) 
            x_train = loaded_data['X_train']
            y_train = loaded_data['Y_train']
            shape = [64, 64, 3]
            classes = 1000
        else:
            print('The requested dataset is currently not supported.')
            sys.exit(0)
        if shape[-1] < 3: #If is not RGB image
            x_train=np.dstack([x_train] * 3)
            # Reshape images as per the tensor format required by tensorflow
            x_train = x_train.reshape(-1, shape[0], shape[1], 3)
        if shape[0] < 48:
            x_train = np.asarray([img_to_array(array_to_img(im, scale=False).resize((48,48))) for im in x_train])
        # elif shape[0] > 56:
        #     x_train = np.asarray([img_to_array(array_to_img(im, scale=False).resize((56,56))) for im in x_train])
        if dataset != "downsample_imagenet":
            x_train = x_train / 255.0
            y_train = to_categorical(y_train)
        # x_test = x_test / 255.0
        # y_test = to_categorical(y_test)
        # np.savez(dataset, x_train, y_train, x_test, y_test) # uncomment this if you want to use test data
        # np.savez(dataset, x_train, y_train) # uncomment this if you wnat to dump processed dataset
    print("shape:", x_train.shape)
    print("preprocess time:", time.time() - start_preprocess)
    if selected_model == "vgg16":
        from tensorflow.keras.applications.vgg16 import VGG16
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=(x_train.shape[1], x_train.shape[2], x_train.shape[3]))
    elif selected_model == "resnet50":
        from tensorflow.keras.applications import ResNet50
        from tensorflow.keras.applications.resnet import preprocess_input
        x_train = preprocess_input(x_train)
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(x_train.shape[1], x_train.shape[2], x_train.shape[3]))
    elif selected_model == "resnet152":
        from tensorflow.keras.applications import ResNet152
        from tensorflow.keras.applications.resnet import preprocess_input
        x_train = preprocess_input(x_train)
        base_model = ResNet152(weights='imagenet', include_top=False, input_shape=(x_train.shape[1], x_train.shape[2], x_train.shape[3]))
    elif selected_model == "mobilenet":
        from tensorflow.keras.applications import MobileNet
        from tensorflow.keras.applications.mobilenet import preprocess_input
        x_train = preprocess_input(x_train)
        base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(x_train.shape[1], x_train.shape[2], x_train.shape[3]))
    else:
        print('The requested model is currently not supported.')
        sys.exit(0)
    for layer in base_model.layers:
        layer.trainable = False
    
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        # tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(classes, activation='softmax')
    ])
    ##or the following:
    # x = Flatten()(base_model.output)
    # x = Dense(classes, activation='softmax')(x)
    # model = Model(inputs=base_model.input, outputs=x)
    if dataset == "downsample_imagenet":
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    else:
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    x_train_ = []
    y_train_= []
    if dataset == "downsample_imagenet":
        x_train_ = x_train[0:30000]
        y_train_ = y_train[0:30000]
    else:
        x_train_ = x_train
        y_train_ = y_train
    print(x_train.shape)
    print(y_train.shape)
    check_pid = str(os.getpid())
    trace_name = "dl_" + dataset + "_" + selected_model + "_" + str(BATCH_SIZE)
    # time.sleep(5)
    if  params['heatmap'] == True:
        damo_trace = "/home/cc/functions/run_bench/playground/"+ trace_name + "/" + trace_name + ".data"
        print("damo_trace file is: ", damo_trace)
        # time.sleep(5)
        subprocess.Popen(["sudo","damo","record", "-s", "1000", "-a", "100000", "-u",
                          "1000000", "-n", "5000", "-m", "6000", "-o", 
                        damo_trace, check_pid])
    if  params['vtune'] == True:
        PROF_DIR = os.path.join(PROF_DIR_BASE, trace_name)
        if os.path.isdir(PROF_DIR):
            shutil.rmtree(PROF_DIR)
        subprocess.Popen([VTUNE, "-collect", "uarch-exploration", "-r", 
                          PROF_DIR, "-target-pid", check_pid])
    # Train the model
    train_start = time.time()
    # x_train = x_train[0:20000]
    # y_train = y_train[0:20000]
    # time.sleep(5)
    # output_file = open("/home/cc/functions/dl/interfer.log", 'w')
    # if  params['inference'] != 0:
    #     for i in range (params['inference']):
    #         subprocess.Popen(['numactl', '--physcpubind', '12,14,16,18,20,22', '--', 'python', '/home/cc/functions/dl/inference.py', '5'], stdout=output_file)
    current_time = datetime.datetime.now()
    print("train start time:", current_time)
    model.fit(x_train_, y_train_, epochs=NB_EPOCHS, batch_size=BATCH_SIZE)
    print("training_time: {:.2f}".format(time.time() - train_start))