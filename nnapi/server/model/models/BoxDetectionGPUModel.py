
from pathlib import Path

def seg2box(class_model, seg_model,params,save=True):

  Ppath = Path(params.file_path)
  img_arr = seg_model.img_loader.load(Ppath)
  model_type = 'B'

  seg_pred_c = class_model.draw_boxes(img_arr,seg_model.model.bbox_coordinates)
  if save:
    new_path = seg_model._saver.save(seg_pred_c, model_type, Ppath)
  return str(new_path), seg_pred_c