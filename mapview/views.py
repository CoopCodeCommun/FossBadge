from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from mapview.models import Marker, MapViewConfig
# Create your views here.

class IndexViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication,]

    def list(self, request):
        context = {
            "markers" : Marker.objects.all(),
            "m_config" : MapViewConfig.get_solo(),
        }
        return render(request, 'mapview_base.html', context)

