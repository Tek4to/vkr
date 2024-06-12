from django.db import models
from django.utils.translation import gettext_lazy as _
from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils.regex_helper import _lazy_re_compile
from django.utils import timezone

from medml import utils


"""Mixins"""

def get_full_name(self):
  """
  Return the first_name plus the last_name, with a space in between.
  """
  full_name = "%s %s %s" % (self.last_name, self.first_name, self.fathers_name)
  return full_name.strip().capitalize()



"""CUSTOM FIELDS"""

class PolicyField(models.CharField):
  def __init__(self, *args, **kwargs):
    kwargs['max_length'] = 16
    super(PolicyField, self).__init__(*args, **kwargs)
    self.validators.append(RegexValidator(

      _lazy_re_compile(r"^\d{16}\Z"),
      message=_("Enter a valid integer."),
      code="invalid",
    ))


class LowerEmailField(models.EmailField):
  def get_prep_value(self, value):
    return super().get_prep_value(value).lower()

dcm_validator = FileExtensionValidator([
  'dcm','png','jpeg','jpg','tiff','tif'
  ])


"""DB MODELS"""

class MedWorker(BaseUser):
  """
  TODO: add patien create permissions
  """
  email = LowerEmailField(_("email address"), unique=True)

  is_remote_worker = models.BooleanField(
    "Удаленный Эксперт",
    default=False
  )

  fathers_name = models.CharField("Отчество", max_length=150, blank=True)
  
  med_organization = models.CharField("Медицинская организация", max_length=512, blank=True)

  job = models.CharField("Должность", max_length=256, blank=True, null=True)

  objects = BaseUserManager()

  expert_details = models.TextField(
    "Описание экспертных качеств",
    default=""
  )

  class Meta:
    permissions = [
      ('add_patient', 'Can add Patient'),
      ('change_patient', 'Can change Patient'),
      ('view_patient', 'Can view Patient'),
    ]
    verbose_name="Мед работник"
    verbose_name_plural = "Мед работники"

  def get_full_name(self) -> str:
    return get_full_name(self)


class UZIDevice(models.Model):
  """
  Аппарат, на котором происходило УЗИ диагностика
  """
  name = models.CharField("Название аппарата", max_length=512)

  class Meta:
    verbose_name="Аппарат УЗИ"
    verbose_name_plural = "Аппараты УЗИ"

  def __str__(self) -> str:
    return f"{self.name}"


class PatientCard(models.Model):
  """
  Информация о том какой пациент посещал какого врача
  и результатах диагностики
  """

  NODULES_CHOICES = (
    ('T', 'Обнаружено новообразование'),
    ('F', 'Без паталогий'),
  )
  
  # Many2Many class
  patient = models.ForeignKey(
    "Patient",
    on_delete=models.SET_NULL,
    related_name="card",
    null=True
  )

  med_worker = models.ForeignKey(
    "MedWorker",
    on_delete=models.SET_NULL,
    related_name="card",
    null=True
  )

  acceptance_datetime = models.DateTimeField('Дата и время приема', auto_now_add=True)

  has_nodules = models.CharField(
    "Узловые новообразования", 
    max_length=128, 
    choices=NODULES_CHOICES, 
    default=NODULES_CHOICES[1][0]
  )
  diagnosis = models.TextField(
    _("Диагноз"), 
    blank=True,
    default=""
  )

  class Meta:
    verbose_name="Карта пациента"
    verbose_name_plural = "Карты пациентов"


class UZIImageBase(models.Model):
  image = None  # change to filefield in child
  image_group = None # change to filefield in child
  # original filename ?

  brightness = models.FloatField(
    "Яркость",
    validators=[MinValueValidator(-1), MaxValueValidator(1)],
    default=0
  )

  contrast = models.FloatField(
    "Контраст",
    validators=[MinValueValidator(-1), MaxValueValidator(1)],
    default=0
  )

  sharpness = models.FloatField(
    "Резкость",
    validators=[MinValueValidator(-1), MaxValueValidator(1)],
    default=0
  )

  image_count = models.IntegerField(
    'Количество снимков',
    validators=[MinValueValidator(0)],
    default=0
  )

  create_date = models.DateTimeField(
    "Дата создания",
    default=timezone.now
  )

  delay_time = models.FloatField(
    "Время обработки",
    default=-1
  )

  viewed_flag = models.BooleanField(
    "Просмотренно",
    default=False
  )

  class Meta:
    abstract = True


class OriginalImage(UZIImageBase):

  image = models.FileField(
    "Cнимок",
    upload_to=utils.originalUZIPath,
    validators=[dcm_validator]
  )

  image_group = models.OneToOneField(
    "UZIImageGroup",
    verbose_name="Карта пациента (снимки)",
    related_name='original_image',
    null=True,
    blank=True,
    on_delete=models.SET_NULL
  )

  class Meta:
    verbose_name="Снимок оригинала"
    verbose_name_plural = "Снимки оригиналов"

class SegmentationImage(UZIImageBase):

  image = models.FileField(
    "Cнимок",
    upload_to=utils.segUZIPath,
    null=True,
    validators=[dcm_validator]
  )

  image_group = models.OneToOneField(
    "UZIImageGroup",
    verbose_name="Карта пациента (снимки)",
    related_name='seg_image',
    null=True,
    blank=True,
    on_delete=models.SET_NULL
  )

  class Meta:
    verbose_name="Снимок Сегмента"
    verbose_name_plural = "Снимки сегментов"

class BoxImage(UZIImageBase):

  image = models.FileField(
    "Cнимок",
    upload_to=utils.boxUZIPath,
    null=True,
    validators=[dcm_validator]
  )

  image_group = models.OneToOneField(
    "UZIImageGroup",
    verbose_name="Карта пациента (снимки)",
    related_name='box_image',
    null=True,
    blank=True,
    on_delete=models.SET_NULL
  )

  class Meta:
    verbose_name="Снимок с боксами"
    verbose_name_plural = "Снимки с боксами"


class UZIImageGroup(models.Model):
  """
  УЗИ картинка пациента
  """
  PROJECTION_TYPE_CHOICES = (
    ('long', 'Продольный'),
    ('cross', 'Поперечный'),
  )

  uzi_device = models.ForeignKey(
    'UZIDevice',
    on_delete=models.SET_NULL,
    null=True
  )

  # projection_type = models.CharField(
  #   "Тип проекции", 
  #   max_length=128, 
  #   choices=PROJECTION_TYPE_CHOICES, 
  #   default=PROJECTION_TYPE_CHOICES[0][0]
  # )

  patient_card = models.ForeignKey(
    'PatientCard',
    on_delete=models.SET_NULL,
    null=True,
    related_name='uzi_images'
  )

  details = models.JSONField(
    'Детали диагностики'
  )

  # nodule_type = models.IntegerField(
  #   "Тип узла",
  #   validators=[MinValueValidator(1), MaxValueValidator(5)],
  #   default=1,
  #   null=True
  # )

  # echo_descr = models.TextField(
  #   "Эхографические признаки",
  #   null=True,
  #   default=""
  # )


  # nodule_1 = models.FloatField(
  #   "Тип 1",
  #   validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
  #   default=0.0
  # )

  # nodule_2 = models.FloatField(
  #   "Тип 2",
  #   validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
  #   default=0.0
  # )

  # nodule_3 = models.FloatField(
  #   "Тип 3",
  #   validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
  #   default=0.0
  # )

  # nodule_4 = models.FloatField(
  #   "Тип 4",
  #   validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
  #   default=0.0
  # )

  # nodule_5 = models.FloatField(
  #   "Тип 5",
  #   validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
  #   default=0.0
  # )

  # nodule_widht = models.FloatField("Ширина", validators=[MinValueValidator(0)], default=1)
  # nodule_height = models.FloatField("Высота", validators=[MinValueValidator(0)], default=1)
  # nodule_length = models.FloatField("Длина", validators=[MinValueValidator(0)], default=1)


  class Meta:
    verbose_name="Группа изображений"
    verbose_name_plural = "Группа УЗИ изображений"


class Patient(models.Model):
  first_name = models.CharField(_("first name"), max_length=150)
  last_name = models.CharField(_("last name"), max_length=150)
  fathers_name = models.CharField("Отчество", max_length=150)

  personal_policy = PolicyField("Полис")
  email = models.EmailField(_("email address"), unique=True)
  is_active = models.BooleanField(_("Пациент активен"), default=True)

  class Meta:
    verbose_name="Пациент"
    verbose_name_plural = "Пациенты"

  def get_full_name(self) -> str:
    return get_full_name(self)

  def __str__(self):
    return self.get_full_name()


class MLModel(models.Model):

  MODEL_TYPES_CHOICES = (
    ('C', 'Модель для классификации'),
    ('S', 'Модель для сегментации'),
    ('B', 'Модель для боксов'),
  )
  PROJECTION_TYPES_CHOICES = (
    ('cross', 'поперечная'),
    ('long', 'продольная'),
    ('all', 'обе'),
  )

  name = models.CharField("Имя модели", max_length=256)
  file = models.FileField(
    "Путь к файлу модели",
    upload_to=utils.mlModelPath
  )
  model_type = models.CharField(
    "Тип модели",
    choices=MODEL_TYPES_CHOICES,
    default=MODEL_TYPES_CHOICES[0][0],
    max_length=1,
  )
  projection_type = models.CharField(
    "Тип проекции",
    choices=PROJECTION_TYPES_CHOICES,
    default=PROJECTION_TYPES_CHOICES[0][0],
    max_length=10,
  )

  class Meta:
    verbose_name="Модель МЛ"
    verbose_name_plural = "Модели МЛ"

