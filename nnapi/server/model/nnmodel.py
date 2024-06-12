from abc import ABC, abstractmethod
from typing import Iterable
from server.settings import settings
from pathlib import Path
from server.model.loaders.modelPreLoader import ModelPreLoaderABC, ZipModelPreLoader


class ModelABC(ABC):

  def __init__(self, model_type: str, projection_type:str='full', model_pre_loader:ModelPreLoaderABC=ZipModelPreLoader) -> None:
    self._model = ... # переменная, в которую загружается модель 
    self.pre_loader = model_pre_loader(model_type, projection_type)
    base_dir = self.pre_loader.load(settings['BASE_PATH'])
    self.load(base_dir)

  @abstractmethod
  def load(self, path: Path) -> None:
    """
    Функция, в которой обределяется структура NN и
    происходит загрузка весов модели в self._model

    params:
      path - путь к файлу, в котором содержатся веса модели
    """
    ...

  @abstractmethod
  def preprocessing(self, path: str) -> object:
    """
    Функция, котороя предобрабатывает изображение к виду, 
    с которым можеn взаимодействовать модель из self._model

    params:
      path - путь к файлу (изображению .tiff/.png), который будет
            использоваться для предсказания

    return - возвращает предобработанное изображение 
    """
    ...

  @abstractmethod
  def predict(self, images: Iterable) -> object:
    """
    Функция, в которой предобработанное изображение подается
    на входы NN (self._model) и возвращается результат работы NN 

    params:
      path - путь к файлу (изображению .tiff/.png), который будет
            использоваться для предсказания

    return - результаты предсказания
    """
    ...
