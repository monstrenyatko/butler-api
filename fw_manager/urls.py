from django.conf.urls import url
from . import views as local_view

urlpatterns = [
    url(r'^firmwares/$', local_view.FirmwareListView.as_view()),
    url(r'^firmwares/(?P<name>[^\s\/]+)/$', local_view.FirmwareDetailView.as_view()),
    url(r'^assignments/$', local_view.FirmwareAssignmentListView.as_view()),
    url(r'^assignments/(?P<username>[^\s\/]+)/$', local_view.FirmwareAssignmentDetailView.as_view()),
    url(r'^upload/(?P<filename>[^\s\/]+)/$', local_view.FirmwareUploadView.as_view()),
    url(r'^update/$', local_view.FirmwareUpdateView.as_view()),
    url(r'^update/(?P<username>[^\s\/]+)/$', local_view.FirmwareUpdateAnonymousView.as_view()),
]
