from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import Sum
from medml.models import BoxImage, OriginalImage, SegmentationImage

# Create your views here.
def index(request:HttpRequest,) -> HttpResponse:
  count = {"orig":0, "segm":0, "box":0}
  #latency = {"total":0, "segm":0, "box":0}

  #count["orig"] = OriginalImage.objects.count()
  count["orig"] = OriginalImage.objects.aggregate(Sum('image_count'))['image_count__sum'] or 0
  #count["segm"] = SegmentationImage.objects.filter(delay_time__gt = -1).count()
  count["box"] = BoxImage.objects.filter(delay_time__gt = -1).aggregate(Sum('image_count'))['image_count__sum'] or 0
  data = "Images_Count{label=\"Original\"} "+str(count["orig"])+"\n"\
         "Images_Count{label=\"Processed\"} "+str(count["box"])+"\n"\
         "Images_In_Process_Count "+str(count["orig"] - count["box"])#+"\n"\
        #"Images_Count{label=\"Segmented\"} "+str(count["segm"])+"\n"\
        #  "NN_Latency{label=\"Segmented\"} "+str(latency["segm"])+"\n"\
        #  "NN_Latency{label=\"Box\"} "+str(latency["box"])+"\n"\
        #  "NN_Latency{label=\"Total\"} "+str(latency["total"])

  return HttpResponse(data, content_type="text/plain")