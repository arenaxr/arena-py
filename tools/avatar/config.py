from tensorflow import keras
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

exp_file='exp.csv'

lmk_file='lmk.csv'

root_dir="face-data-latest/synthetic"

output_dim = 52
input_dim = 136
batch_size = 128 

epochs=1000

svfile="lmk2exp_model"

