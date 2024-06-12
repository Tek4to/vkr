from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from medemail import tasks
from medemail import serializers as ser



class EmailAPIView(CreateAPIView):

  serializer_class = ser.EmailPostSerializer
  permission_classes = [AllowAny]


  def perform_create(self, serializer):
    email = serializer.save()
    tasks.send_email.delay(email.id)
