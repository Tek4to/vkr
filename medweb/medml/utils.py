from django.conf import settings
from django.core.mail import EmailMessage
from datetime import date
import hashlib
import os
import tifffile as tiff
import pydicom
import io
from tempfile import NamedTemporaryFile

from pathlib import Path
import requests


"""
  See docs, why dynamic not working
  https://docs.djangoproject.com/en/4.1/topics/migrations/#migration-serializing
  Any function or method reference (e.g. datetime.datetime.today) (must be in module’s top-level scope)


  class UploadPathConstructor:
    def __init__(self, basedir: str) -> None:
      self.basedir: str = basedir

    def uzi_upload_path(self, obj, filename: str):
      filen, filee = os.path.splitext(filename)
      h = hashlib.sha256(filen).hexdigest()[:settings.IMAGE_NAME_MAX_CHARS]
      return f"{self.basedir}/%Y/{obj.patient.id}/{h}.{filee}"
"""

def _makePath(obj, filename: str, basedir: str):
  filen, filee = os.path.splitext(filename)
  filee = filee.lower()
  h = hashlib.sha256(filen.encode('utf-8')).hexdigest()[:settings.IMAGE_NAME_MAX_CHARS]
  if filee in {'.jpeg','.jpg'}:
    filee = '.png'
  return f"{basedir}/{date.today().year}/{obj.image_group.patient_card.patient.id}/{h}{filee}"


def originalUZIPath(obj, filename: str):
  return _makePath(obj, filename, "originalUZI")


def boxUZIPath(obj, filename: str):
  return _makePath(obj, filename, "boxUZI")

def segUZIPath(obj, filename: str):
  return _makePath(obj, filename, "segUZI")

def mlModelPath(obj, filename: str):
  filen, filee = os.path.splitext(filename)
  h = hashlib.sha256(filen.encode('utf-8')).hexdigest()[:settings.IMAGE_NAME_MAX_CHARS]

  return f"nnModel/{date.today().year}/{h}{filee}"

def getFields(obj, has_id=True, add_name=''):
  d = {f"{add_name}{f.name}":getattr(obj, f.name) for f in obj._meta.fields}
  if not has_id:
    d.pop(f"{add_name}id")
  return d

def sendImgToPredict(file_path: str, model_type: str, projection_type: str):
  path = settings.MEDIA_ROOT_PATH / file_path # TODO: Chnage depedencies on settings.MEDIA_ROOT
  data = requests.post('http://nnapi:8001/predict', json={
    'file_path':str(path), 
    'model_type':model_type,
    'projection_type':projection_type
    })
  d = Path(data.json())
  dd = d.relative_to(settings.MEDIA_ROOT_PATH)
  return str(dd)

def sendToMl(file_path: str, url: str, projection_type: str) -> dict:
  path = settings.MEDIA_ROOT_PATH / file_path
  data =requests.post(f'http://nnapi:8001/predict/{url}', json={
    'file_path':str(path), 
    'projection_type':projection_type
    })

  d = data.json()
  return d

def updateModels(file_path: str, model_type:str, projection_type: str) -> dict:
  path = settings.MEDIA_ROOT_PATH / file_path
  data =requests.post(f'http://nnapi:8001/update/', json={
    'file_path':str(path), 
    'projection_type':projection_type,
    'model_type': model_type
    })

  d = data.json()
  return d

def send_2_email(email, original_path, seg_path, box_path):
  email_msg = EmailMessage(
    'Subject',
    'Your images',
    settings.WEB_EMAIL,
    [email],
    headers={'Reply-To':settings.WEB_EMAIL}
  )
  email_msg.attach_file(original_path)
  email_msg.attach_file(seg_path)
  email_msg.attach_file(box_path)
  email_msg.send()


def updateClassesToGroup(classes, group):
  for key in classes:
    group.details[f'nodule_{key}'] = classes[key]
  group.details['nodule_type'] = int(max(classes.items(),key=lambda x: x[1])[0])

def in_mem_image_pre_saver(image):
  fbase, filee = os.path.splitext(image.name)
  filee = filee.lower()
  if filee in {'.tif', '.tiff'}:
    # fixing tiff images
    tmp = NamedTemporaryFile()
    try:
      with image.open() as inp:
        t = tiff.imread(inp)
      tiff.imwrite(tmp, t, compression ='zlib')
      image.file = tmp
    except tiff.TiffFileError as e:
      raise AttributeError(f'Битый .tif файл. {e}')
    return image, t.shape[0]
  elif filee in {'.dcm'}:
    # convert .dcm to tiff
    tmp = NamedTemporaryFile()
    try:
      with image.open() as inp:
        t = pydicom.dcmread(inp)
      img_size = t.pixel_array.shape[0]
      tiff.imwrite(tmp, t.pixel_array, compression ='zlib')
      image.file = tmp
      image.name = fbase + '.tif'
    except:
      raise AttributeError(f'Битый .dcm файл.')
    return image, img_size
  return image, 1
