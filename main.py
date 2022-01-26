import colorsys

import numpy as np
from keras import backend as K
from keras.models import load_model

from yolo5.model import yolo_eval, Mish
from yolo5.utils import letterbox_image
import os
from keras.utils import multi_gpu_model


name_classes = ['Defect'] # Названия классов
num_classes = len(name_classes) # Количество классов
input_shape = (416, 416) # Размерность входного изображения
path = 'D:/TVEL/defect'

# Массив используемых анкоров (в пикселях). Используетя по 3 анкора на каждый из 3 уровней сеток
# данные значения коррелируются с размерностью входного изображения input_shape
anchors = np.array([[10, 13], [16, 30], [33, 23], [30, 61], [62, 45], [59, 119], [116, 90], [156, 198], [373, 326]])
num_anchors = len(anchors) # Сохраняем количество анкоров
with open("./data/images/data.yaml", 'r') as stream:
    num_classes = str(yaml.safe_load(stream)['nc'])




@register_line_cell_magic
def writetemplate(line, cell):
    with open(line, 'w') as f:
        f.write(cell.format(**globals()))



'''
    Функция создания полной модели
        Входные параметры:       
          input_shape - размерность входного изображения для модели YOLO
          num_anchors - общее количество анкоров   
          use_weights - использовать ли предобученные веса         
          weights_path - путь к сохраненным весам модели  
'''



