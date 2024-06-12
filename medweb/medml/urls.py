from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from medml import views


urlpatterns = [
    path('test/', views.Test1.as_view()),
    path('auth/register/', views.RegistrationView.as_view(), name='registration'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('model/update/<int:id>', views.ModelUpdateView.as_view(), name='model_update'),

    path('med_worker/', include([
      path('list/', views.MedWorkerListView.as_view(), name='med_worker_list_view'),
      # Изменить информацию о мед работнике
      path('update/<int:id>', views.MedWorkerChangeView.as_view(), name='med_worker_update'),
      # Инфа о текущем враже, отдельно инфа о пациентах его и отдельно инфа о карточках пациента
      path('u/patients/<int:id>', views.MedWorkerTableGetView.as_view(), name='med_worker_table'), # UNUSED
      # Для Start Page - инфа только о последенй карточке
      # TODO: Добавить фильтры
      path('patients/<int:id>', views.MedWorkerPatientsTableView.as_view(), name='med_worker_patients_table'),
    ])),

    path('patient/', include([
      path('list/', views.PatientListView.as_view(), name='patient_list_view'),
      # Создание пациента и карточки
      path('create/<int:id>', views.PatientAndCardCreateGeneric.as_view(), name='patient_create'),
      # Изменение только информации о пациенте и его конкретной карточки 
      path('update/<int:id>/', views.PatientAndCardUpdateView.as_view(), name='patient_update'),
      # # инфа о карточках пациента и если были снимки, то инфа о сниках (без самих снимков), иначе инфа о всех каторчках
      # path('shots/<int:id>/', views.PatientShotsTableView.as_view(), name='patient_shots_table'),

      # инфа о карточках пациента и если были снимки, то инфа о сниках (без самих снимков), иначе инфа о всех каторчках
      path('shots/<int:id>/', views.PatientShotsTable2View.as_view(), name='patient_shots_table_2'),
    ])),

    path('uzi/', include([
      # Получить список исследований УЗИ по ид
      path('ids/', views.UZIIdsView.as_view(), name='uzi_ids'),
      # Список аппаратов УЗИ
      path('devices/', views.UZIDeviceView.as_view(), name='uzi_devices'),
      # # Создать Группу изображений и добавить снимок оригинала
      # path('create/', views.UZIImageCreateView.as_view(), name='uzi_group_create'),
      # Создать Группу изображений и добавить снимок оригинала стандартному пользователю
      path('create/user/', views.UZIImagePatientCreateView.as_view(), name='uzi_group_patinet_create'),
      # Информация об одной группе снимков ()
      path('<int:id>/', views.UziImageShowView.as_view(), name='uzi_image_show'),
      # # Обновление всей страницы с информацией о приеме
      # path('<int:id>/update', views.UZIShowUpdateView.as_view(), name='uzi_show_update'),
      # Обновление оригинального снимка (только параметры отображения)
      path('update/origin/<int:id>', views.UZIOriginImageUpdateView.as_view(), name='uzi_update_origin'),
      # Обновление box снимка (только параметры отображения)
      path('update/box/<int:id>', views.UZIBoxImageUpdateView.as_view(), name='uzi_update_predict'),
      # Обновление сегментации снимка (только параметры отображения)null
      path('update/segmentation/<int:id>', views.UZISegmentationImageUpdateView.as_view(), name='uzi_update_mask'),
      # Обновление картинки сегментации и класса TIRADS
      path('update/seg_group/<int:id>', views.UZISegmentationAndImageGroupView.as_view(), name='uzi_mask_and_group_update'),

      # Создать Группу изображений и добавить снимок оригинала
      path('create/', views.UZIImageCreate2View.as_view(), name='uzi_group_create_2'),
      # Обновление всей страницы с информацией о приеме
      path('<int:id>/update/', views.UZIShowUpdate2View.as_view(), name='uzi_show_update'),

    ])),
]
