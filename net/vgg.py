'''
Author: Rich, wu
'''

import os

import tensorflow as tf
from keras.models import Model
from keras.layers import Input, BatchNormalization, Reshape
from keras import backend as K
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Activation
from keras.layers import GlobalAveragePooling2D, AveragePooling2D, GlobalMaxPooling2D
from keras.regularizers import l2
from keras.engine import get_source_inputs
from keras.utils import get_file, layer_utils
from keras_applications.imagenet_utils import _obtain_input_shape

import warnings




def VGG16(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000, weights_file=None, l2_norm=5e-4):

    VGG16_WEIGHTS_PATH = 'https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg16_weights_th_dim_ordering_th_kernels.h5'
    VGG16_WEIGHTS_PATH_NO_TOP = 'https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg16_weights_th_dim_ordering_th_kernels_notop.h5'

    input_shape = _obtain_input_shape(input_shape, default_size=224, min_size=48, data_format=K.image_data_format(), require_flatten=include_top)
    
    if input_tensor is None:
        img_input = Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            img_input = Input(tensor=input_tensor, shape=input_shape)
        else:
            img_input = input_tensor
    
    # Block1
    x = Conv2D(64, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv1_1')(img_input)
    x = Conv2D(64, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv1_2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool1')(x)

    # Block2
    x = Conv2D(128, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv2_1')(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv2_2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool2')(x)

    # Block3
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_1')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_2')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_3')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool3')(x)

    # Block4
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_3')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool4')(x)

    # Block5
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_3')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool5')(x)

    if include_top:
        x = Flatten(name='flatten')(x)
        x = Dense(4096, name='fc6')(x)
        x = Activation('relu', name='fc6/relu')(x)
        x = Dense(4096, name='fc7')(x)
        x = Activation('relu', name='fc7/relu')(x)
        x = Dense(classes, name='fc8')(x)
        x = Activation('softmax', name='fc8/softmax')(x)
    else:
        if pooling == 'avg':
            x = GlobalAveragePooling2D()(x)
        elif pooling == 'max':
            x = GlobalMaxPooling2D()(x)
    
    if input_tensor is not None:
        inputs = get_source_inputs(input_tensor)
    else:
        inputs = img_input
    
    model = Model(inputs, x, name='vggFace_vgg16')
    model.summary()
    if  weights == 'imagenet':
        if include_top:
            weights_path = get_file('vgg16_weights_th_dim_ordering_th_kernels.h5',
                                    VGG16_WEIGHTS_PATH,
                                    cache_subdir='./models')
        elif weights_file is not None:
            weights_path = weights_file
        else:
            weights_path = get_file('vgg16_weights_th_dim_ordering_th_kernels_notop.h5',
                                    VGG16_WEIGHTS_PATH_NO_TOP,
                                    cache_dir="./models")
    
    model.load_weights(weights_path, by_name=True)

    if K.backend() == 'theano':
        layer_utils.convert_all_kernels_in_model(model)
    
    if K.image_data_format() == 'channel_first':
        if include_top:
            maxpool = model.get_layer(name='pool5')
            shape = maxpool.output_shape[1:]
            dense = model.get_layer(name='fc6')
            layer_utils.convert_dense_weights_data_format(dense, shape, 'channels_first')

        if K.backend() == 'tensorflow':
            warnings.warn('You are using the TensorFlow backend, yet you '
                              'are using the Theano '
                              'image data format convention '
                              '(`image_data_format="channels_first"`). '
                              'For best performance, set '
                              '`image_data_format="channels_last"` in '
                              'your Keras config '
                              'at ~/.keras/keras.json.')
    return model


def VGG19(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000, weights_file=None, l2_norm=5e-4):

    WEIGHTS_PATH = 'https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg19_weights_tf_dim_ordering_tf_kernels.h5'
    NONE_WEIGHTS_PATH = 'https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5'

    input_shape = _obtain_input_shape(input_shape, default_size=224, min_size=48, data_format=K.image_data_format(), require_flatten=include_top)

    if input_tensor is None:
        img_input = Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            img_input = Input(tensor=input_tensor, shape=input_shape)
        else:
            img_input = input_tensor
    
    # Block1
    x = Conv2D(64, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv1_1')(img_input)
    x = Conv2D(64, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv1_2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool1')(x)

    # Block2
    x = Conv2D(128, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv2_1')(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv2_2')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool2')(x)

    # Block3
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_1')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_2')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_3')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv3_4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool3')(x)

    # Block4
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_3')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv4_4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool4')(x)

    # Block5
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_1')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_2')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_3')(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(l2_norm), name='conv5_4')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='pool5')(x)

    if include_top:
        x = Flatten(name='flatten')(x)
        x = Dense(4096, name='fc6')(x)
        x = Activation('relu', name='fc6/relu')(x)
        x = Dense(4096, name='fc7')(x)
        x = Activation('relu', name='fc7/relu')(x)
        x = Dense(classes, name='fc8')(x)
        x = Activation('softmax', name='fc8/softmax')(x)
    else:
        if pooling == 'avg':
            x = GlobalAveragePooling2D()(x)
        elif pooling == 'max':
            x = GlobalMaxPooling2D()(x)
    
    if input_tensor is not None:
        inputs = get_source_inputs(input_tensor)
    else:
        inputs = img_input
    
    model = Model(inputs, x, name='vggFace_vgg16')
    model.summary()
    if  weights == 'imagenet':
        if include_top:
            weights_path = get_file('vgg19_weights_tf_dim_ordering_tf_kernels.h5',
                                    WEIGHTS_PATH,
                                    cache_subdir='./models')
        elif weights_file is not None:
            weights_path = weights_file
        else:
            weights_path = get_file('/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5',
                                    NONE_WEIGHTS_PATH,
                                    cache_dir="./models")
    
    model.load_weights(weights_path, by_name=True)

    if K.backend() == 'theano':
        layer_utils.convert_all_kernels_in_model(model)
    
    if K.image_data_format() == 'channel_first':
        if include_top:
            maxpool = model.get_layer(name='pool5')
            shape = maxpool.output_shape[1:]
            dense = model.get_layer(name='fc6')
            layer_utils.convert_dense_weights_data_format(dense, shape, 'channels_first')

        if K.backend() == 'tensorflow':
            warnings.warn('You are using the TensorFlow backend, yet you '
                              'are using the Theano '
                              'image data format convention '
                              '(`image_data_format="channels_first"`). '
                              'For best performance, set '
                              '`image_data_format="channels_last"` in '
                              'your Keras config '
                              'at ~/.keras/keras.json.')
    return model