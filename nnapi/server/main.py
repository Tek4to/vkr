from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import time
from typing import *

from server.model.defaultModels import DefalutModels, seg2box

class PredictPath(BaseModel):
  file_path: Path
  model_type: str
  projection_type: str


class PredictSegPath(BaseModel):
  file_path: Path
  projection_type: str

class LoadPath(BaseModel):
  file_path: Path
  projection_type: str
  model_type: str

class SegResponse(BaseModel):
  path: Path
  classes: Dict[str, float]

class BoxResponse(BaseModel):
  path: Path

class AllResponse(BaseModel):
  seg_path: Path
  box_path: Path
  classes: Dict[str, float]
  d_seg: float
  d_box: float

app = FastAPI()

@app.post('/predict')
async def predict(params: PredictPath) -> Path:
  new_path, _ = (DefalutModels[params.model_type][params.projection_type]
    .predict(params.file_path, params.model_type)
  )
  return new_path

  
@app.post('/predict/all')
async def predict(params: PredictSegPath) -> AllResponse:
  st = time.time()
  seg_model = DefalutModels['S'][params.projection_type]
  new_path, seg_pred = (seg_model
    .predict(params.file_path, 'S', save=True)
  )
  d_seg = time.time() - st
  class_model = DefalutModels['C'][params.projection_type]
  classes = class_model.predict(seg_model.model.rois, seg_model.model.img_type)
  
  # seg_pred_c = class_model.draw_boxes(seg_pred, seg_model.model.bbox_coordinates)
  # new_path = seg_model.save(seg_pred, params.file_path, 'S')
  box_path, box_img = seg2box(class_model, seg_model, params)
  d_box = time.time() - st
  cc = class_model.norm_classes(classes)
  print(time.time() - st, cc, new_path, box_path)
  return {'seg_path':new_path, 'box_path':box_path, 'classes':cc, 'd_seg':d_seg, 'd_box':d_box}

@app.post('/predict/segmentation')
async def predict(params: PredictSegPath) -> SegResponse:
  seg_model = DefalutModels['S'][params.projection_type]
  new_path, seg_pred = (seg_model
    .predict(params.file_path, 'S', save=False)
  )
  class_model = DefalutModels['C'][params.projection_type]
  classes = class_model.predict(seg_model.model.rois, seg_model.model.img_type)
  
  # seg_pred_c = class_model.draw_boxes(seg_pred, seg_model.model.bbox_coordinates)
  new_path = seg_model.save(seg_pred, params.file_path, 'S')
  return {'path':new_path, 'classes':class_model.norm_classes(classes)}

@app.post('/predict/box')
async def predict(params: PredictSegPath) -> BoxResponse:
  seg_model = DefalutModels['B'][params.projection_type]
  new_path, _ = (seg_model
    .predict(params.file_path, 'B')
  )
  return {'path':new_path}


@app.post('/update')
async def update(params: LoadPath):
  # TODO: change type chacking for classification
  if params.model_type == 'C':
    path = DefalutModels[params.model_type][params.projection_type].pre_loader.load(params.file_path)
  else:
    path = params.file_path

  return DefalutModels[params.model_type][params.projection_type].load(
    # params.file_paths, params.model_type, params.projection_type
    path
  )