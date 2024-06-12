from abc import ABC, abstractmethod
from typing import Iterable
from pathlib import Path
from PIL import Image

import pickle
import hashlib
import tifffile as tiff
import imageio
import pydicom

from server.settings import settings
import uuid


class ImgSaverABC(ABC):

  TYPES_PATH = {
    'B': "boxUZI", # TODO: CHANGE CONSTATNST IN MDEML.UTILS
    'S': "segUZI"
  }
  ORIGINAL_NAME = "originalUZI"

  @abstractmethod
  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    pass

  def gen_path(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    paths = list(basedir.parts)
    base_path, to_folder_path = paths[1:-4], paths[-3:-1]
    new_path = Path(basedir.parts[0])
    for p in base_path:
      new_path /= p
    new_path /= self.TYPES_PATH[model_type]
    for p in to_folder_path:
      new_path /= p

    new_path = self.__gen_path(new_path, basedir.suffix)
    print('save path: ', new_path)
    return new_path

  def perform_save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    """Called before save"""
    new_path = self.gen_path(obj, model_type, basedir)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    return new_path
  
  def __gen_path(self, path: Path, ext: str):
    ndone = True
    h = self.__gen_filename()
    extra = ""
    while ndone:
      tmp = path / f"{h}{extra}{ext}"
      if not tmp.is_file():
        return tmp
      extra = self.__gen_filename(8)

  def __gen_filename(self, max_chars: int=settings['IMAGE_NAME_MAX_CHARS']):
    return hashlib.sha256(uuid.uuid1().bytes).hexdigest()[:max_chars]


class PngSaver(ImgSaverABC):

  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    new_path = self.perform_save(obj, model_type, basedir)
    image = Image.fromarray(obj[0])
    image.save(new_path, 'png')
    return new_path

class JpegSaver(ImgSaverABC):

  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    new_path = self.perform_save(obj, model_type, basedir)
    image = Image.fromarray(obj[0])
    image.save(new_path, 'jpeg')
    return new_path

class TiffSaver(ImgSaverABC):

  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    new_path = self.perform_save(obj, model_type, basedir)
    tiff.imwrite(new_path, obj, compression ='zlib')
    return new_path

class DicomSaver(ImgSaverABC):
  """This class doesn't works"""
  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    new_path = self.perform_save(obj, model_type, basedir)
    pydicom.dcmwrite(new_path, obj) # not so ease... CHANGE!
    return new_path


class ImgeoSaver(ImgSaverABC):

  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    new_path = self.perform_save(obj, model_type, basedir)
    imageio.mimwrite(new_path, obj)
    return new_path


class ImgSaver(ImgSaverABC):

  def __init__(self) -> None:
    tiffSaver = TiffSaver()
    jpgSaver = JpegSaver()
    self.__savers: dict[str, ImgSaverABC] = {
      '.png': PngSaver(),
      '.tiff': tiffSaver,
      '.tif': tiffSaver,
      '.jpeg': jpgSaver,
      '.jpg': jpgSaver,
      '.dcm': tiffSaver,
    }

  def save(self, obj: Iterable, model_type: str, basedir: Path) -> Path:
    ext = basedir.suffix.lower()
    if ext not in self.__savers:
      raise AttributeError('Нет такого файлового загрузчика')
    return self.__savers[ext].save(obj, model_type, basedir)

if __name__ == '__main__':
  from loaders.ImgLoader import ImgLoader
  il = ImgLoader()
  bp = Path('./media/segUZI/2022/1/3510d999b0.png')
  a = il.load(bp)
  iS = ImgSaver()
  np = iS.save(a, 'S', bp)
  print(np)
