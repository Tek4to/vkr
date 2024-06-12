from django.urls import path, include
from medemail import views


urlpatterns = [
  path('send_email/',views.EmailAPIView.as_view(), name='send_email')
]