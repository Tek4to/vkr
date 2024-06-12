from server.model.savers.ImgSaver import ImgSaver 
from server.model.models.SegmentationModel import ModelABC, SegmentationModel
from server.model.models.ClassificationModel import ResnetModel
from server.model.models.BoxDetectionGPUModel import seg2box
from server.model.ServerModel import ServerModel
from server.model.loaders.ImgLoader import ImgLoader

from typing import *



DefaultImgLoader = ImgLoader()
DefaultSaver = ImgSaver()
# DefalutImgeoSaver = ImgeoSaver()

MODEL_DIR = {
  'S': 'segUZI',
  'B': 'boxUZI',
  'C': 'classUZI',
}

# DefaultClassificationModel = ClassificationModel()
# TrackingModelDefault = TrackingModel(MODEL_DIR['B'], 'full')

DefalutModels: Dict[str, Dict[str,ModelABC]] = {
  'C': {
    'cross': ResnetModel(MODEL_DIR['C'],'cross'),
    'long': ResnetModel(MODEL_DIR['C'],'long'),
  },
  'S': {
    'cross': ServerModel(SegmentationModel(MODEL_DIR['S'],'cross'), DefaultSaver, DefaultImgLoader),
    'long': ServerModel(SegmentationModel(MODEL_DIR['S'],'long'), DefaultSaver, DefaultImgLoader),
  },
  # 'B': {
  #   'cross': ServerModel(TrackingModelDefault, DefaultSaver, DefaultImgLoader),
  #   'long': ServerModel(TrackingModelDefault, DefaultSaver, DefaultImgLoader),
  # },
}
print('all models were loaded!')