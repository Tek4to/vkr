from rest_framework import serializers as ser
from django.core.validators import EmailValidator

from medml.models import (
  MedWorker, Patient, PatientCard,
  UZIImageGroup, UZIImageBase, UZIDevice,
  OriginalImage, BoxImage, SegmentationImage,
  MLModel, dcm_validator
)
from medml import utils
from medml.json_base.forms.UZIGroupForm import (
  UZIGroupForm,
  UZIForm
)

from django.db.models import F, Value, JSONField, Func
from django.db.models.expressions import CombinedExpression

from PIL import Image
from pathlib import Path
import os


"""MIXINS"""

class RelativeURLMixin:

  def to_representation(self, instance):
    response = super(RelativeURLMixin, self).to_representation(instance)
    if instance.image:
      response['image'] = instance.image.url
    return response


"""Patients' Serializers"""

class PatientSerializer(ser.ModelSerializer):

  class Meta:
    model = Patient
    fields = '__all__'
    extra_kwargs ={
      'email': {
        'validators': [EmailValidator()]
      }
    }

  def create(self, validated_data):
    try:
      obj = Patient.objects.get(email=validated_data['email'])
    except:
      obj = Patient.objects.create(**validated_data)
    return obj


class UZIDeviceSerializer(ser.ModelSerializer):
  class Meta:
    model = UZIDevice
    fields = '__all__'


"""MedWorkers' Serializers"""

class MedWorkerRegistrationSerializer(ser.ModelSerializer):

  password1 = ser.CharField(
    write_only=True,
    required=True,
    style={'input_type': 'password', 'placeholder': 'Пароль'}
  )

  password2 = ser.CharField(
    write_only=True,
    required=True,
    style={'input_type': 'password', 'placeholder': 'Повторите Пароль'}
  )

  class Meta:
    model = MedWorker
    fields = [
      'email', 
      'last_name', 
      'first_name', 
      'fathers_name', 
      'med_organization',
      'password1',
      'password2',
      ]
    # add extra validators MinLength TypeCheck
    extra_kwargs = {
      'last_name': {'required': True},
      'first_name': {'required': True},
      'fathers_name': {'required': True},
      'med_organization': {'required': True},
    }

  def create(self, validated_data: dict):
    password1 = validated_data.pop('password1')
    password2 = validated_data.pop('password2')
    if password1 != password2:
      raise ValueError("Пароли должны совпадать")
    user: MedWorker = MedWorker.objects.create_user(**validated_data, password=password1)
    return user
  

class MedWorkerCommonSerializer(ser.ModelSerializer):

  class Meta:
    model = MedWorker
    fields = [
      'last_name', 
      'first_name', 
      'fathers_name', 
      'med_organization',
      'job',
      'is_remote_worker',
      'expert_details',
      'id'
    ]

  def to_representation(self, instance):
    ret = super().to_representation(instance)
    if not ret['is_remote_worker']:
      ret['expert_details'] = ""
    return ret


class PatientCardItemSerializer(ser.ModelSerializer):
  """UNUSED"""
  class Meta:
    model = PatientCard
    exclude = ['med_worker']


class MedWorkerTableSerializer(ser.Serializer):
  """
    Read-only serializer
    UNUSED
  """
  cards = PatientCardItemSerializer(many=True)
  med_worker = MedWorkerCommonSerializer()

  def __new__(cls, *args, **kwargs):
    kwargs['many'] = False
    return super(MedWorkerTableSerializer, cls).__new__(cls,*args, **kwargs)

  def to_representation(self, instance):
    med_worker = self.context['medworker']
    patients = {}
    for c in instance:
      if c.patient.id not in patients:
        patients[c.patient.id] = PatientSerializer().to_representation(c.patient) 
    ret = super().to_representation({'cards':instance, 'med_worker':med_worker})
    ret['patients'] = patients
    return ret


class PatientCardTableItemSerializer(ser.ModelSerializer):
  patient = PatientSerializer()

  class Meta:
    model = PatientCard
    exclude = ['med_worker']

  def to_representation(self, instance):
    return super().to_representation(instance)


class MedWorkerPatientsTableSerializer(ser.Serializer):
  cards = PatientCardTableItemSerializer(many=True)
  med_worker = MedWorkerCommonSerializer()

  def __new__(cls, *args, **kwargs):
    kwargs['many'] = False
    return super(MedWorkerPatientsTableSerializer, cls).__new__(cls,*args, **kwargs)

  def to_representation(self, instance):
    med_worker = self.context['medworker']
    ret = super().to_representation({'cards':instance, 'med_worker':med_worker})
    return ret


"""UIZs' serializers"""

class ShotsSerializer(ser.ModelSerializer):
  class Meta:
    model = PatientCard
    exclude = [
      'patient','med_worker','id'
    ]

class UZIImageGroupModelSerializer(ser.ModelSerializer):
  patient_card = ShotsSerializer()
  class Meta:
    model = UZIImageGroup
    fields = '__all__'
    # exclude = [
    #   'nodule_1',
    #   'nodule_2','nodule_3',
    #   'nodule_4','nodule_5'
    # ]

  def to_representation(self, instance):
    ret = super().to_representation(instance)
    details = ret.pop('details')
    [details.pop(key) for key in [
      'nodule_1',
      'nodule_2','nodule_3',
      'nodule_4','nodule_5'
    ]]
    ret.update(details)
    ret['uzi_device'] = getattr(instance.uzi_device, 'name', None)
    ret.update(ret.pop('patient_card'))
    return ret


class UZIImageGroupModel2Serializer(ser.ModelSerializer):
  patient_card = ShotsSerializer()
  class Meta:
    model = UZIImageGroup
    fields = '__all__'

  def to_representation(self, instance):
    ret = super().to_representation(instance)
    details = ret.pop('details')
    ret.update(details)
    ret['uzi_device'] = getattr(instance.uzi_device, 'name', None)
    ret.update(ret.pop('patient_card'))
    return ret


"""Patients' serializers"""


class PatientCardSerializer(ser.ModelSerializer):

  class Meta:
    model = PatientCard
    exclude = ['patient', 'med_worker']


class PatientAndCardSerializer(ser.Serializer):
  patient = PatientSerializer()
  card = PatientCardSerializer()

  def create(self, validated_data):
    med_worker = self.context['med_worker']
    patient = self.fields['patient'].create(validated_data['patient'])
    card_data:dict = validated_data['card']
    card_data['med_worker'] = med_worker
    card_data['patient'] = patient
    card = self.fields['card'].create(card_data)
    return {"patient": patient, "card": card }

  def update(self, instance, validated_data):
    patient = instance['patient']
    card = instance['card']
    self.inst_update(patient, validated_data['patient'])
    self.inst_update(card, validated_data['card'])
    patient.save()
    card.save()
    return {"patient": patient, "card": card }

  def inst_update(self, ins, values):
    for i in values:
      setattr(ins,i,values[i])



class PatientTableSerializer(ser.Serializer):
  patient = PatientSerializer()
  shots = UZIImageGroupModelSerializer(many=True)

  def __new__(cls, *args, **kwargs):
    kwargs['many'] = False
    return super(PatientTableSerializer, cls).__new__(cls,*args, **kwargs)

  def to_representation(self, instance):
    patient = self.context['patient']
    if not instance:
      qs = PatientCard.objects.filter(patient=patient).all()
      instance = [UZIImageGroup(patient_card=q) for q in qs]
    ret = super().to_representation({
      'shots':instance,
      'patient':patient
    })
    return ret


class PatientTable2Serializer(ser.Serializer):
  patient = PatientSerializer()
  shots = UZIImageGroupModel2Serializer(many=True)

  def __new__(cls, *args, **kwargs):
    kwargs['many'] = False
    return super(PatientTable2Serializer, cls).__new__(cls,*args, **kwargs)

  def to_representation(self, instance):
    patient = self.context['patient']
    if not instance:
      qs = PatientCard.objects.filter(patient=patient).all()
      instance = [UZIImageGroup(patient_card=q) for q in qs]
    ret = super().to_representation({
      'shots':instance,
      'patient':patient
    })
    return ret


"""UZIS' serizlisers"""

class UZIImageCreateSerializer(ser.ModelSerializer):
  original_image = ser.FileField(required=True, write_only=True,validators=[dcm_validator])
  projection_type = ser.ChoiceField(
    choices=UZIImageGroup.PROJECTION_TYPE_CHOICES,
    default=UZIImageGroup.PROJECTION_TYPE_CHOICES[0][0]
  )

  class Meta:
    model = UZIImageGroup
    fields = (
      'uzi_device',
      'projection_type',
      'patient_card',
      'original_image'
    )

  def create(self, validated_data):
    # TODO: CHANGE to return ID of image_group
    image = validated_data.pop('original_image')
    nimage, count = utils.in_mem_image_pre_saver(image)
    ssr = UZIGroupForm(data={'projection_type':validated_data.pop('projection_type')})
    ssr.is_valid(raise_exception=True)
    validated_data['details'] = ssr.validated_data
    image_group = super().create(validated_data)
    originaImage = OriginalImage.objects.create(image=nimage, image_group=image_group, image_count=count)
    return {'image_group': image_group, 'image': originaImage}

class UZIImageCreate2Serializer(ser.ModelSerializer):
  original_image = ser.FileField(required=True, write_only=True,validators=[dcm_validator])
  projection_type = ser.ChoiceField(
    choices=UZIImageGroup.PROJECTION_TYPE_CHOICES,
    default=UZIImageGroup.PROJECTION_TYPE_CHOICES[0][0]
  )

  class Meta:
    model = UZIImageGroup
    fields = (
      'uzi_device',
      'projection_type',
      'patient_card',
      'original_image'
    )

  def create(self, validated_data):
    # TODO: CHANGE to return ID of image_group
    image = validated_data.pop('original_image')
    nimage, count = utils.in_mem_image_pre_saver(image)
    ssr = UZIForm(data={'projection_type':validated_data.pop('projection_type')})
    ssr.is_valid(raise_exception=True)
    validated_data['details'] = ssr.validated_data
    image_group = super().create(validated_data)
    originaImage = OriginalImage.objects.create(image=nimage, image_group=image_group, image_count=count)
    return {'image_group': image_group, 'image': originaImage}
  


class UZIOriginalImageSerializer(RelativeURLMixin, ser.ModelSerializer):
  class Meta:
    model = OriginalImage
    fields = '__all__'


class UZISegmentationImageSerializer(RelativeURLMixin, ser.ModelSerializer):
  class Meta:
    model = SegmentationImage
    fields = '__all__'


class UZIBoxImageSerializer(RelativeURLMixin, ser.ModelSerializer):
  class Meta:
    model = BoxImage
    fields = '__all__'


class UZIImageStackSerializer(ser.Serializer):
  """support class"""
  original = UZIOriginalImageSerializer()
  box = UZIBoxImageSerializer(allow_null=True)
  segmentation = UZISegmentationImageSerializer(allow_null=True)

class UZIImageGroupAllSerializer(ser.ModelSerializer):

  class Meta:
    model = UZIImageGroup
    exclude = [
      'uzi_device',
      'patient_card'
    ]
    extra_kwargs = {
      'nodule_1': {'read_only': True},
      'nodule_2': {'read_only': True},
      'nodule_3': {'read_only': True},
      'nodule_4': {'read_only': True},
      'nodule_5': {'read_only': True},
    }


class UZIImageGroupSupprotSerializer(ser.Serializer):
  patient = PatientSerializer()
  uzi_device = UZIDeviceSerializer()
  patient_card = PatientCardSerializer()
  image_group = UZIImageGroupAllSerializer()

  UZI_DEV_PREFIX = 'uzi_device_'

  def to_representation(self, obj:UZIImageGroup):
    sz = super().to_representation(
        {
        'patient':obj.patient_card.patient, 
        'uzi_device': obj.uzi_device,
        'patient_card': obj.patient_card,
        'image_group': obj
        })
    patient_card = sz.pop('patient_card')
    uzi_device = sz.pop('uzi_device')
    image_group = sz.pop('image_group')
    sz.update({f"{self.UZI_DEV_PREFIX}{f}": uzi_device[f] for f in uzi_device})
    sz.update(patient_card)
    sz['patient_card_id'] = sz.pop('id')
    sz.update(image_group)
    return sz

class UZIImageGroupGetSerializer(ser.Serializer):

  # TODO: REVIEW
  # TODO: ADD UPDATE
  images = UZIImageStackSerializer()
  info = UZIImageGroupSupprotSerializer()
  
  def to_representation(self, instance):
    images = {
      'original': getattr(instance, 'original_image', None),
      'segmentation': getattr(instance, 'seg_image', None),
      'box': getattr(instance, 'box_image', None),
    }
    return super().to_representation({'images':images,'info':instance})


class PatientCardUpdateSerializer(ser.ModelSerializer):
  class Meta:
    model = PatientCard
    fields = [
      'patient',
      'acceptance_datetime',
      'has_nodules',
      'diagnosis'
      ]
    extra_kwargs = {
      'patient': {'allow_null': False},
    }
    

class UZIShowUpdateSerializer(ser.ModelSerializer):
  patient_card = PatientCardUpdateSerializer()

  class Meta:
    model = UZIImageGroup
    fields = '__all__'
    extra_kwargs = {
      'uzi_device': {'allow_null': False},
      'patient_card': {'allow_null': False},
      'nodule_widht': {'default': 1},
      'nodule_height': {'default': 1},
      'nodule_length': {'default': 1},
      'echo_descr': {'allow_blank': True}
    }
  
  def to_internal_value(self, data):
    return super().to_internal_value(data)


  def update(self, instance, validated_data):
    patient_card = validated_data.pop('patient_card')
    details = validated_data.pop('details')

    ssr = UZIGroupForm(data=details)
    ssr.is_valid(raise_exception=True)
    validated_data['details'] = ssr.validated_data
    [validated_data['details'].pop(i,None) for i in [
      'nodule_1',
      'nodule_2','nodule_3',
      'nodule_4','nodule_5'
    ]]
    PatientCardUpdateSerializer().update(instance.patient_card, patient_card)
    return super().update(instance, validated_data)
  

class UZIShowUpdate2Serializer(ser.ModelSerializer):
  patient_card = PatientCardUpdateSerializer(required=False)

  class Meta:
    model = UZIImageGroup
    fields = '__all__'
    extra_kwargs = {
      'uzi_device': {'required': False},
    }
    


  def update(self, instance, validated_data):
    patient_card = validated_data.pop('patient_card', None)
    details = validated_data.pop('details')
    in_keys = details.keys()

    ssr = UZIForm(data=details)
    ssr.is_valid(raise_exception=True)
    vd = {key:ssr.validated_data[key] for key in in_keys}
    validated_data['details'] = CombinedExpression(
      F('details'),
      "||",
      Value(vd, JSONField())
    )
    if patient_card is not None:
      PatientCardUpdateSerializer().update(instance.patient_card, patient_card)
    ret = super().update(instance, validated_data)
    ret.details = vd
    return ret



class UZIImageGroupInfoSerialier(ser.Serializer):

  info = UZIImageGroupSupprotSerializer()


class UZISegmentationUpdateSerializer(ser.ModelSerializer):
  
  class Meta:
    model = SegmentationImage
    fields = ['pk','image']


class UZIImageGroupUpdateSerializer(ser.ModelSerializer):

  class Meta:
    model = UZIImageGroup
    fields = [
      'pk',
      # 'nodule_type'
    ]

class UZISegmentationAndImageGroupUpdateSerializer(ser.Serializer):
  segmentation_image = UZISegmentationUpdateSerializer()
  group = UZIImageGroupUpdateSerializer()

  def update(self, instance, validated_data):
    segmentation_image = self.fields['segmentation_image'].update(instance['segmentation_image'], validated_data['segmentation_image'])
    group = self.fields['group'].update(instance['group'], validated_data['group'])
    return {'segmentation_image':segmentation_image, 'group':group}


class UZIUpdateOriginalImageSerializer(ser.ModelSerializer):
  class Meta:
    model = OriginalImage
    exclude = ['image', 'image_group']


class UZIUpdateSegmentedImageSerializer(ser.ModelSerializer):
  class Meta:
    model = SegmentationImage
    exclude = ['image', 'image_group']


class UZIUpdateBoxedImageSerializer(ser.ModelSerializer):
  class Meta:
    model = BoxImage
    exclude = ['image', 'image_group']



"""ML"""

class MLModelSerializer(ser.ModelSerializer):
  class Meta:
    model = MLModel
    fields= '__all__'

"""Patient"""
class UZIImagePatientCreateSerializer(ser.Serializer):
  shot_data = UZIImageCreateSerializer()
  email = ser.EmailField()

  def create(self, validated_data):
    email = validated_data['email']
    aaa = self.fields['shot_data']
    ret = aaa.create(validated_data=validated_data['shot_data'])
    ret.update({'email':email})
    return ret
