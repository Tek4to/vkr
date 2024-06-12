from celery import shared_task
from time import sleep
from pathlib import Path

import requests


from medml.models import SegmentationImage, BoxImage
from medml.utils import sendToMl, updateClassesToGroup, updateModels, send_2_email
from django.utils import timezone
from django.conf import settings
import datetime

# @shared_task()
# def call_predict(file_path: str, model_type: str, projection_type: str, id: int):
#   # new_path = apps.get_app_config('medml').ml_defaults[model_type][projection_type].predict(Path(file_path), model_type)
#   new_path = sendImgToPredict(file_path, model_type, projection_type)
#   OBJ = IMAGES_MODELS[model_type]
#   obj = OBJ.objects.get(id=id)
#   obj.image = new_path
#   obj.save()
#   return
  

@shared_task
def predict_all(file_path: str, projection_type: str, id: int, img_count:int):
  print('all_prediction:', file_path, id)
  data = sendToMl(file_path, 'all', projection_type)
  seg_model = (SegmentationImage.objects
    .filter(id=id)
    .select_related('image_group')
  )[0]
  box_model = (BoxImage.objects
    .filter(id=id)
  )[0]
  image_group = seg_model.image_group
  updateClassesToGroup(data['classes'], image_group)
  db = datetime.timedelta(seconds=data['d_box'])
  t = timezone.now() - db
  dd = Path(data['seg_path']).relative_to(settings.MEDIA_ROOT_PATH) 
  seg_model.image = str(dd)
  seg_model.image_count = img_count
  seg_model.create_date = t + datetime.timedelta(seconds=data['d_seg'])
  seg_model.delay_time = data['d_seg']
  dd = Path(data['box_path']).relative_to(settings.MEDIA_ROOT_PATH) 
  box_model.image = str(dd)
  box_model.image_count = img_count
  box_model.create_date = timezone.now()
  box_model.delay_time = data['d_box']
  
  seg_model.save()
  box_model.save()
  image_group.save()

@shared_task()
def predict_seg(file_path: str, projection_type: str, id: int, img_count:int):
  data = sendToMl(file_path, 'segmentation', projection_type)
  model = (SegmentationImage.objects
    .filter(id=id)
    .select_related('image_group')
  )[0]
  image_group = model.image_group
  updateClassesToGroup(data['classes'], image_group)
  dd = Path(data['path']).relative_to(settings.MEDIA_ROOT_PATH) 
  model.image = str(dd)
  model.image_count = img_count
  model.save()
  image_group.save()
  
@shared_task()
def predict_box(file_path: str, projection_type: str, id: int, img_count:int):
  data = sendToMl(file_path, 'box', projection_type)
  model = (BoxImage.objects
    .filter(id=id)
  )[0]
  dd = Path(data['path']).relative_to(settings.MEDIA_ROOT_PATH) 
  model.image = str(dd)
  model.image_count = img_count
  model.save()
  
@shared_task()
def update_model_weights(file_path: str, model_type: str, projection_type: str):
  res = updateModels(file_path, model_type, projection_type)


@shared_task()
def add_to_db():
  sleep(5)
  r = requests.post('http://web:8000/api/patient/create/', json={
    "patient": {
        "first_name": "Oleg",
        "last_name": "Olegov",
        "fathers_name": "Oleg",
        "personal_policy": "1234123412341234",
        "email": "asdfs@asda.as",
        "is_active": False
    },
    "card": {
        "has_nodules": "T",
        "diagnosis": "F"
    }
  })

@shared_task()
def images_to_email(file_path: str, projection_type: str, box_id: int, seg_id: int, email: str):

  data = sendToMl(file_path, 'segmentation', projection_type)
  model = (SegmentationImage.objects
    .filter(id=seg_id)
    .select_related('image_group')
  )[0]
  image_group = model.image_group
  updateClassesToGroup(data['classes'], image_group)
  dd1 = Path(data['path']).relative_to(settings.MEDIA_ROOT_PATH) 
  model.image = str(dd1)
  model.save()

  data = sendToMl(file_path, 'box', projection_type)
  model = (BoxImage.objects
    .filter(id=box_id)
  )[0]
  dd2 = Path(data['path']).relative_to(settings.MEDIA_ROOT_PATH) 
  model.image = str(dd2)
  model.save()

  image_group.save()
  dd0 = settings.MEDIA_ROOT_PATH / Path(file_path)
  send_2_email(email,dd0,settings.MEDIA_ROOT_PATH/dd1,settings.MEDIA_ROOT_PATH/dd2)