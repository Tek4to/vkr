from server.model.savers.ImgSaver import ImgSaverABC 
from server.model.loaders.ImgLoader import ImgLoaderABC 
from server.model.models.SegmentationModel import ModelABC
from pathlib import Path


class ServerModel:

  def __init__(self, model: ModelABC, saver:ImgSaverABC, img_loader: ImgLoaderABC) -> None:
    self.model = model
    self._saver = saver
    self.img_loader = img_loader

  # def load(self, path: str, model_type:str, projection_type: str) -> None:
  def load(self, path: str) -> None:
    """
    Функция, в которой обределяется структура NN и
    происходит загрузка весов модели в self._model

    params:
      path - путь к файлу, в котором содержатся веса модели
    """
    tmp_path = self.model.pre_loader.load(path)
    self.model.load(tmp_path)
    # self.model.load(path)

  def save(self, obj: object, path: str, model_type:str):
    Ppath = Path(path)
    return str(self._saver.save(obj, model_type, Ppath))

  def predict(self, path: str, model_type:str, save=True):
    """
    Функция, в которой предобработанное изображение подается
    на входы NN (self._model) и возвращается результат работы NN 

    params:
      path - путь к файлу (изображению .tiff/.png), который будет
            использоваться для предсказания

    return - результаты предсказания
    """
    Ppath = Path(path)
    img_arr = self.img_loader.load(Ppath)
    # print('!!! image_array', img_arr)
    obj = self.model.predict(img_arr)
    # print('!!! image_obj', obj, obj.shape)
    new_path = ""
    if save:
      new_path = self._saver.save(obj, model_type, Ppath)
    return str(new_path), obj