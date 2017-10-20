from django.conf.urls import url
from . import views as local_view

urlpatterns = [
    url(r'^fingerprints/(?P<host>[^\s\/]+)/$', local_view.CertificateFingerprintView.as_view()),
    url(r'^client/(?P<type>[^\s\/]+)/$', local_view.ClientCertificateView.as_view()),
    url(r'^client/(?P<type>[^\s\/]+)/(?P<form>[^\s\/]+)/$', local_view.ClientCertificateView.as_view()),
    url(r'^ca/$', local_view.CaCertificateView.as_view()),
    url(r'^ca/(?P<form>[^\s\/]+)/$', local_view.CaCertificateView.as_view()),
]
