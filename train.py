import numpy as np
import os
import time
from datetime import datetime
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.layers import ReLU
from keras.utils import plot_model
from utils import define_model, prepare_dataset
import tensorflow as tf
from keras.backend import tensorflow_backend

def train(iteration=3, DATASET='ALL', crop_size=128, need_au=True, ACTIVATION='ReLU', dropout=0.1, batch_size=32,
          repeat=4, minimum_kernel=32, epochs=200):
    model_name = f"Final_Emer_Iteration_{iteration}_cropsize_{crop_size}_epochs_{epochs}"

    print("Model : %s" % model_name)

    prepare_dataset.prepareDataset(DATASET)

    activation = globals()[ACTIVATION]
    model = define_model.get_unet(minimum_kernel=minimum_kernel, do=dropout, activation=activation, iteration=iteration)

    try:
        os.makedirs(f"trained_model/{DATASET}/", exist_ok=True)
        os.makedirs(f"logs/{DATASET}/", exist_ok=True)
    except:
        pass

    load_path = f"trained_model/{DATASET}/{model_name}_weights.best.hdf5"
    try:
        model.load_weights(load_path, by_name=True)
    except:
        pass

    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y-%m-%d---%H-%M-%S")

    tensorboard = TensorBoard(
        log_dir=f"logs/{DATASET}/Final_Emer-Iteration_{iteration}-Cropsize_{crop_size}-Epochs_{epochs}---{date_time}",
        histogram_freq=0, batch_size=32, write_graph=True, write_grads=True,
        write_images=True, embeddings_freq=0, embeddings_layer_names=None,
        embeddings_metadata=None, embeddings_data=None, update_freq='epoch')

    save_path = f"trained_model/{DATASET}/{model_name}.hdf5"
    checkpoint = ModelCheckpoint(save_path, monitor='seg_final_out_loss', verbose=1, save_best_only=True, mode='min')

    data_generator = define_model.Generator(batch_size, repeat, DATASET)

    history = model.fit_generator(data_generator.gen(au=need_au, crop_size=crop_size, iteration=iteration),
                                  epochs=epochs, verbose=1,
                                  steps_per_epoch=100 * data_generator.n // batch_size,
                                  use_multiprocessing=True, workers=8,
                                  callbacks=[tensorboard, checkpoint])


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"]="0"
    config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
    session = tf.Session(config=config)
    tensorflow_backend.set_session(session)

    #epochs>100 will be enough, but slower
    train(batch_size=8, iteration=3,
        epochs=120, crop_size=128) 
