from celery import shared_task
from django.utils import timezone
from pathlib import Path

from django.conf import settings
from medemail.models import MedEmail
from medemail.utils import BaseEmailCreator

EMAIL_CREATORS = {
  'base': BaseEmailCreator()
}

@shared_task
def send_email(email_id: MedEmail, email_creator_key='base'):
  email_creator = EMAIL_CREATORS[email_creator_key]
  email = MedEmail.objects.get(id=email_id)
  email_msg = email_creator.quick_create(email)
  email_msg.send()
  email.send_date = timezone.now()
  email.save()