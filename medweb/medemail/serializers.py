from rest_framework import serializers as ser

from medemail.models import MedEmail


class EmailPostSerializer(ser.ModelSerializer):
  
  class Meta:
    model = MedEmail
    exclude = ['send_date']
