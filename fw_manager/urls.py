from django.conf.urls import url
from . import views as local_view

urlpatterns = [
    url(r'^update/$', local_view.FirmwareUpdateView.as_view()),
]