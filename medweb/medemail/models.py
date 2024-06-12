from django.db import models

from medml import models as med_models


class MedEmail(models.Model):
  """
  Класс для сохранения истории сообщений
  """
  to_email = med_models.LowerEmailField(
    verbose_name='Кому'
  )
  
  from_email = models.ForeignKey(
    med_models.MedWorker,
    models.CASCADE,
    verbose_name='От кого')

  details = models.ForeignKey(
    med_models.UZIImageGroup,
    on_delete=models.CASCADE,
    verbose_name='Детали сообщения'
  )

  create_date = models.DateTimeField(
    verbose_name="Дата создания сообщения",
    auto_now_add=True
  )

  send_date = models.DateTimeField(
    verbose_name="Дата отправки сообещения",
    null=True
  )

  class Meta:
    verbose_name="Сообщение"
    verbose_name_plural = "Сообщения"

    