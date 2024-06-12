import json
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework.renderers import JSONRenderer

from django.db.models import Max, Subquery, Prefetch
from django.db import connection, reset_queries
from django.http import Http404

from medml import filters
from medml import serializers as ser
from medml import models
from medml import tasks
from medml.json_base.forms.UZIGroupForm import UZIGroupForm



"""MedWorkers' VIEWS"""
class RegistrationView(CreateAPIView):

  serializer_class = ser.MedWorkerRegistrationSerializer
  permission_classes = [AllowAny]


class MedWorkerChangeView(mixins.RetrieveModelMixin, UpdateAPIView):
  serializer_class = ser.MedWorkerCommonSerializer

  def get_object(self):
    try:
      return models.MedWorker.objects.get(id=self.kwargs['id'])
    except:
      raise Http404

  def perform_update(self, serializer):
    return super().perform_update(serializer)

  def get(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)

  def put(self, request, *args, **kwargs):
    return self.patch(request, *args, **kwargs)

  def patch(self, request, *args, **kwargs):
    if request.user.id is self.kwargs['id']:
      return super().patch(request, *args, **kwargs)
    return Response(status=status.HTTP_403_FORBIDDEN)


class MedWorkerTableGetView(ListAPIView):
  """UNSUSED"""
  serializer_class = ser.MedWorkerTableSerializer

  def get_medworker(self):
    try:
      self.medworker = models.MedWorker.objects.get(id=self.kwargs['id'])
      return self.medworker
    except:
      raise Http404

  def get_serializer_context(self):
    # TODO: remove one bd request
    medworker = self.get_medworker()
    ret = super().get_serializer_context()
    ret.update({'medworker':medworker})
    return ret

  def get_queryset(self):
    qs = models.PatientCard.objects.filter(
      med_worker__id=self.kwargs['id']
      ).select_related('patient')
    return qs


class MedWorkerPatientsTableView(ListAPIView):

  serializer_class = ser.MedWorkerPatientsTableSerializer

  # TODO: add to mixin
  def get_medworker(self):
    try:
      self.medworker = models.MedWorker.objects.get(id=self.kwargs['id'])
      return self.medworker
    except:
      raise Http404

  def get_serializer_context(self):
    # TODO: remove one bd request
    medworker = self.get_medworker()
    ret = super().get_serializer_context()
    ret.update({'medworker':medworker})
    return ret

  def get_queryset(self):
    qs = models.PatientCard.objects.filter(
      med_worker__id=self.kwargs['id'],
      ).select_related('patient')
    qs2 = (qs.values('patient_id')
      .annotate(max_ids=Max('id'))
    )
    qs = (qs.filter(
      id__in=qs2.values('max_ids')
    ))
    return qs

class MedWorkerListView(ListAPIView):
  queryset = models.MedWorker.objects.all()
  serializer_class = ser.MedWorkerCommonSerializer
  filterset_class = filters.MedWorkerListFilter



"""Patients"""


class PatientAndCardCreateGeneric(CreateAPIView):
  serializer_class = ser.PatientAndCardSerializer

  def get_serializer_context(self):
    ret = super().get_serializer_context()
    ret['med_worker'] = models.MedWorker.objects.get(id=self.kwargs['id'])
    return ret

  # def get_permissions(self):
  #   return [IsAuthenticated()]
  #   # return []

  def create(self, request, *args, **kwargs):
    return super().create(request, *args, **kwargs)


class PatientAndCardUpdateView(mixins.RetrieveModelMixin, UpdateAPIView):
  serializer_class = ser.PatientAndCardSerializer
  lookup_url_kwarg = 'id'

  def get_permissions(self):
    """Change permission for PUT and PATCH"""
    return super().get_permissions()

  def get_object(self):
    obj_id = self.kwargs.get(self.lookup_url_kwarg)
    obj = models.PatientCard.objects.select_related('patient').filter(id=obj_id)
    try:
      card = obj[0]
    except IndexError as er:
      raise Http404
    patient = card.patient
    ret = {'card':card, 'patient':patient}
    return ret

  def get(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)

  def patch(self, request, *args, **kwargs):
    return super().patch(request, *args, **kwargs)

  def put(self, request, *args, **kwargs):
    kwargs['partial'] = True
    a = super().put(request, *args, **kwargs)
    return a


class PatientShotsTableView(ListAPIView):

  serializer_class = ser.PatientTableSerializer
  

  def get_serializer_context(self):
    ctx = super().get_serializer_context()
    ctx['patient'] = models.Patient.objects.filter(id=self.kwargs['id'])[0]
    return ctx

  def get_queryset(self):
    qs = (
      models.UZIImageGroup.objects
        .select_related('uzi_device', 'patient_card')
        .filter(patient_card__patient__id=self.kwargs['id'])
    )
    
    return qs

  def list(self, request, *args, **kwargs):
    try:
      l = super().list(request, *args, **kwargs)
      return l
    except IndexError:
      return Response(status=status.HTTP_404_NOT_FOUND)

class PatientShotsTable2View(ListAPIView):

  serializer_class = ser.PatientTable2Serializer
  

  def get_serializer_context(self):
    ctx = super().get_serializer_context()
    ctx['patient'] = models.Patient.objects.filter(id=self.kwargs['id'])[0]
    return ctx

  def get_queryset(self):
    qs = (
      models.UZIImageGroup.objects
        .select_related('uzi_device', 'patient_card')
        .filter(patient_card__patient__id=self.kwargs['id'])
    )
    
    return qs

  def list(self, request, *args, **kwargs):
    try:
      l = super().list(request, *args, **kwargs)
      return l
    except IndexError:
      return Response(status=status.HTTP_404_NOT_FOUND)


class PatientListView(ListAPIView):
  queryset = models.Patient.objects.all()
  serializer_class = ser.PatientSerializer
  filterset_class = filters.PatientListFilter

"""UZIs' views"""

class UZIImageCreateView(CreateAPIView):
  serializer_class = ser.UZIImageCreateSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return Response(data, status=status.HTTP_201_CREATED, headers=headers)

  def perform_create(self, serializer):
    d = serializer.save()
    
    image_group = d['image_group']
    original: models.OriginalImage = d['image'] # TODO: changes with nnapi
    segImg = models.SegmentationImage.objects.create(image_group=image_group)
    boxImg = models.BoxImage.objects.create(image_group=image_group)
    tasks.predict_all.delay(
      original.image.path, 
      projection_type=image_group.details['projection_type'], 
      id=boxImg.id,
      img_count=original.image_count
    )
    return {'segmentation_id': segImg.id, 'box_id': boxImg.id, 'image_group_id': image_group.id}

class UZIImageCreate2View(CreateAPIView):
  serializer_class = ser.UZIImageCreate2Serializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return Response(data, status=status.HTTP_201_CREATED, headers=headers)

  def perform_create(self, serializer):
    d = serializer.save()
    
    image_group = d['image_group']
    original: models.OriginalImage = d['image'] # TODO: changes with nnapi
    segImg = models.SegmentationImage.objects.create(image_group=image_group)
    boxImg = models.BoxImage.objects.create(image_group=image_group)
    tasks.predict_all.delay(
      original.image.path, 
      projection_type=image_group.details['projection_type'], 
      id=boxImg.id,
      img_count=original.image_count
    )
    return {'segmentation_id': segImg.id, 'box_id': boxImg.id, 'image_group_id': image_group.id}
        


class UziImageShowView(RetrieveAPIView):

  serializer_class = ser.UZIImageGroupGetSerializer

  def get_object(self):
    try:
      return self.get_queryset()[0]
    except IndexError as er:
      raise Http404

  def get_queryset(self):
    return (models.UZIImageGroup.objects.filter(id=self.kwargs['id'])
      .select_related('uzi_device', 'patient_card', 'original_image', 'seg_image', 'box_image')
      .prefetch_related('patient_card__patient')
    )


class UZISegmentationAndImageGroupView(mixins.RetrieveModelMixin,UpdateAPIView):
  serializer_class = ser.UZISegmentationAndImageGroupUpdateSerializer

  def get_object(self):
    qs = self.get_queryset()
    try:
      seg = qs[0]
      group = seg.image_group
      ret = {'segmentation_image':seg,'group':group}
      return ret
    except:
      return None
  
  def get_queryset(self):
    qs = (models.SegmentationImage.objects
      .filter(id=self.kwargs['id'])
      .select_related('image_group')
    )
    return qs
  

  def get(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)

  def put(self, request, *args, **kwargs):
    return self.partial_update(request, *args, **kwargs)

  def patch(self, request, *args, **kwargs):
    return self.partial_update(request, *args, **kwargs)


class UZIOriginImageUpdateView(UpdateAPIView):
  queryset = models.OriginalImage.objects.all()
  serializer_class = ser.UZIUpdateOriginalImageSerializer
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'id'

class UZISegmentationImageUpdateView(UpdateAPIView):
  queryset = models.SegmentationImage.objects.all()
  serializer_class = ser.UZIUpdateSegmentedImageSerializer
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'id'

class UZIBoxImageUpdateView(UpdateAPIView):
  queryset = models.BoxImage.objects.all()
  serializer_class = ser.UZIUpdateBoxedImageSerializer
  permission_classes = [IsAuthenticated]
  lookup_url_kwarg = 'id'

class UZIDeviceView(ListAPIView):
  queryset = models.UZIDevice.objects.all()
  serializer_class = ser.UZIDeviceSerializer


class UZIIdsView(ListAPIView):
  serializer_class = ser.UZIImageGroupSupprotSerializer
  
  def get_queryset(self):
    ids = json.loads(self.request.query_params.get('ids', ""))
    return (models.UZIImageGroup.objects.filter(id__in=ids)
      .select_related('uzi_device', 'patient_card')
      .prefetch_related('patient_card__patient')
    )

  def list(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())

    page = self.paginate_queryset(queryset)
    if page is not None:
      serializer = self.get_serializer(page, many=True)
      # print(len(serializer.data))
      return self.get_paginated_response(self.list2dict(serializer.data))

    serializer = self.get_serializer(queryset, many=True)
    return Response(self.list2dict(serializer.data))

  def list2dict(self, data, lookup='id'):
    return {di[lookup]:di for di in data}


class UZIShowUpdateView(UpdateAPIView):
  """TODO: FIX 5 DB REQUESTS"""
  serializer_class = ser.UZIShowUpdateSerializer

  def get_object(self):
    try:
      return self.get_queryset()[0]
    except IndexError as er:
      raise Http404

  def get_queryset(self):
    return (models.UZIImageGroup.objects.filter(id=self.kwargs['id'])
      .select_related('patient_card')
    )
  
  def put(self, request, *args, **kwargs):
    return super().put(request, *args, **kwargs)


class UZIShowUpdate2View(UpdateAPIView):
  serializer_class = ser.UZIShowUpdate2Serializer

  def get_object(self):
    try:
      return self.get_queryset()[0]
    except IndexError as er:
      raise Http404

  def get_queryset(self):
    return (models.UZIImageGroup.objects.filter(id=self.kwargs['id'])
      .select_related('patient_card')
    )
  
  def put(self, request, *args, **kwargs):
    return super().put(request, *args, **kwargs)


class ModelUpdateView(CreateAPIView):
  serializer_class = ser.MLModelSerializer
  permission_classes = [IsAuthenticated]

  def get_object(self):
    qs = self.get_queryset()
    try:
      seg = qs[0]
      return seg
    except:
      return None
  
  def get_queryset(self):
    qs = (models.MLModel.objects
      .filter(id=self.kwargs['id'])
    )
    return qs
  
  def post(self, request: Request, *args, **kwargs):
    if request.POST:
      nnmodel = self.get_object()
      if nnmodel:
        tasks.update_model_weights.delay(
          nnmodel.file.path,
          nnmodel.model_type,
          nnmodel.projection_type
        )
    
    return Response(status=status.HTTP_201_CREATED)


"""Patients"""

class UZIImagePatientCreateView(CreateAPIView):
  serializer_class = ser.UZIImagePatientCreateSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return Response(data, status=status.HTTP_201_CREATED, headers=headers)

  def perform_create(self, serializer):
    d = serializer.save()
    
    image_group = d['image_group']
    original: models.OriginalImage = d['image'] # TODO: changes with nnapi
    segImg = models.SegmentationImage.objects.create(image_group=image_group)
    boxImg = models.BoxImage.objects.create(image_group=image_group)
    tasks.images_to_email.delay(
      original.image.path, 
      projection_type=image_group.projection_type, 
      box_id=boxImg.id,
      seg_id=segImg.id,
      email=d['email']
    )
    return {'segmentation_id': segImg.id, 'box_id': boxImg.id, 'image_group_id': image_group.id}
     
class Test1(CreateAPIView):
  serializer_class = UZIGroupForm
