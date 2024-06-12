from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable
import numpy as np
from PIL import Image
import pydicom


class ImgLoaderABC(ABC):
  
  @abstractmethod
  def load(self, base_path: Path) -> Iterable:
    pass


class TiffLoader(ImgLoaderABC):

  def load(self, base_path: Path) -> Iterable:
    images = []
    image = Image.open(base_path)
    i = 0
    while True:
      try:
        image.seek(i)
        image_array = np.array(image)
        images.append(image_array)
        i += 1
      except EOFError:
        break
    return np.array(images)


class PngLoader(ImgLoaderABC):

  def load(self, base_path: Path) -> Iterable:
    image = Image.open(base_path)
    images = [np.array(image.convert('RGB'))]
    return np.array(images)

class DicomLoader(ImgLoaderABC):

  def load(self, base_path: Path) -> Iterable:
    image = pydicom.dcmread(base_path)
    return image.pixel_array


class ImgLoader(ImgLoaderABC):

  def __init__(self) -> None:
    tiffLoader = TiffLoader()
    pngLoader = PngLoader()
    self.__loaders: dict[str, ImgLoaderABC] = {
      '.png': pngLoader,
      '.tiff': tiffLoader,
      '.tif': tiffLoader,
      '.jpeg': pngLoader,
      '.jpg': pngLoader,
      '.dcm': DicomLoader(),
    }

  def load(self, base_path: Path) -> Iterable:
    path = Path(base_path)
    ext = path.suffix.lower()
    if ext not in self.__loaders:
      raise AttributeError('Нет такого файлового загрузчика')
    return self.__loaders[ext].load(path)



if __name__ == '__main__':
  il = ImgLoader()
  a = il.load(Path('./media/segUZI/2022/1/3510d999b0.png'))
  a = il.load(Path('./media/originalUZI/2022/2/a44d5c4f08.tif'))
  import matplotlib.pyplot as plt
  plt.imshow(a[0], cmap='binary')
  plt.show()
  print(a.shape, a)