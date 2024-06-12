from abc import ABC, abstractmethod
from pathlib import Path
import os
import shutil
import zipfile

from server.settings import settings


class ModelPreLoaderABC(ABC):

  def __init__(self, model_type:str, projection_type: str, tmp_dir:str='tmp/') -> None:
    self.tmp_dir: Path = settings['BASE_MODEL_PATH'] / model_type / tmp_dir / projection_type

  @abstractmethod
  def load(self, base_path: str) -> Path:
    pass


class ZipModelPreLoader(ModelPreLoaderABC):

  def load(self, base_path: str) -> Path:
    zip_path = Path(base_path)
    if zip_path.suffix != '.zip':
      raise AttributeError("It's not a .zip archive!")

    if os.path.isdir(self.tmp_dir) and len(os.listdir(self.tmp_dir)):
      shutil.rmtree(self.tmp_dir, ignore_errors=False)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      self.tmp_dir.mkdir(parents=True, exist_ok=True)
      zip_ref.extractall(self.tmp_dir)

    print(self.tmp_dir)
    return self.tmp_dir 

if __name__ == '__main__':
  zip_path = "/media/newking/LinuxHdd6/MainHDD/work/cascade.zip"
  ziper = ZipModelPreLoader('segUZI/')
  ziper.load(zip_path)