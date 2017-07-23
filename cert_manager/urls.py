from django.conf.urls import url
from . import views as local_view

urlpatterns = [
    url(r'^fingerprints/(?P<name>\S+)/$', local_view.CertificateFingerprintView.as_view()),
]