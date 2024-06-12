
from pathlib import Path
from django.core.mail import EmailMessage
from medemail.models import MedEmail
from django.conf import settings


class BaseEmailCreator:
  def __init__(self, subject='Subject',body='body', *args, **kwargs) -> None:
    self.subject = subject
    self.body = body

  def quick_create(self, email: MedEmail):
    email_msg = self.create(email)
    email_msg = self.attach_images(email,email_msg)
    return email_msg

  def create(self,email: MedEmail):
    email_msg = EmailMessage(
      self.subject,
      self.body,
      settings.WEB_EMAIL,
      [email.to_email],
      headers={'Reply-To':settings.WEB_EMAIL}
    )
    return email_msg

  def attach_images(self, email: MedEmail, email_msg: EmailMessage):
    image_group = email.details
    original_path = image_group.original_image.image.path
    seg_path = image_group.seg_image.image.path
    box_path = image_group.box_image.image.path
    email_msg.attach_file(original_path)
    email_msg.attach_file(seg_path)
    email_msg.attach_file(box_path)
    return email_msg

  def send(self, email_msg: EmailMessage):
    email_msg.send()