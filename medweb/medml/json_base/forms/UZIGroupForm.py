from rest_framework.serializers import BaseSerializer, ModelSerializer
from rest_framework import serializers as ser
from medml.models import UZIImageGroup
from collections import OrderedDict

class UZIGroupForm(ModelSerializer):

  def __init__(self, instance=None, data=..., **kwargs):
    super().__init__(instance, data, **kwargs)

  projection_type = ser.ChoiceField(
    choices=UZIImageGroup.PROJECTION_TYPE_CHOICES,
    default=UZIImageGroup.PROJECTION_TYPE_CHOICES[0][0]
  )

  nodule_type = ser.IntegerField(
    min_value=1,
    max_value=5,
    default=1,
    allow_null=True
  )

  echo_descr = ser.CharField(
    default="",
    allow_null=True
  )

  nodule_1 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_2 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_3 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_4 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_5 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )

  nodule_width = ser.FloatField(
    default=1,
    min_value=0,
  )
  nodule_height = ser.FloatField(
    default=1,
    min_value=0,
  )
  nodule_length = ser.FloatField(
    default=1,
    min_value=0,
  )

  class Meta:
    model = UZIImageGroup
    # fields = ['projection_type']
    exclude = ['details']

  def create(self, validated_data):
    ll = set(["projection_type","nodule_type","echo_descr",
          "nodule_1","nodule_2","nodule_3",
          "nodule_4","nodule_5","nodule_width",
          "nodule_height","nodule_length"])
    details = {
      i:validated_data.pop('i') for i in ll
    }
    validated_data['details'] = details
    return super().create(validated_data)


class UZIForm(ModelSerializer):
  projection_type = ser.ChoiceField(
    choices=UZIImageGroup.PROJECTION_TYPE_CHOICES,
    default=UZIImageGroup.PROJECTION_TYPE_CHOICES[0][0]
  )

  profile = ser.CharField(default="чёткие, ровные")

  right_length = ser.FloatField(min_value=0, default=0)
  right_width = ser.FloatField(min_value=0, default=0)
  right_depth = ser.FloatField(min_value=0, default=0)

  left_length = ser.FloatField(min_value=0, default=0)
  left_width = ser.FloatField(min_value=0, default=0)
  left_depth = ser.FloatField(min_value=0, default=0)

  isthmus = ser.FloatField(min_value=0, default=0)

  cdk = ser.CharField(default="не измена")
  position = ser.CharField(default="обычное")
  structure = ser.CharField(default="однородная")
  echogenicity = ser.CharField(default="средняя")

  additional_data = ser.CharField(default="нет")
  rln = ser.CharField(default="нет")
  result = ser.CharField(default="без динамики")
  
  nodule_type = ser.IntegerField(
    min_value=1,
    max_value=5,
    default=1,
    allow_null=True
  )
  
  nodule_1 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_2 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_3 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_4 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )
  nodule_5 = ser.FloatField(
    default=0,
    min_value=0,
    max_value=1
  )


  class Meta:
    model = UZIImageGroup
    exclude = ['details']

  def create(self, validated_data):
    ll = set(["projection_type","profile","right_length","right_width",
          "right_depth","left_length","left_width",
          "left_depth","isthmus","cdk",
          "position","structure","echogenicity",
          "additional_data","rln","result",
          "nodule_type","nodule_1","nodule_2",
          "nodule_3","nodule_4","nodule_5"])
    details = {
      i:validated_data.pop('i') for i in ll
    }
    validated_data['details'] = details
    return super().create(validated_data)
