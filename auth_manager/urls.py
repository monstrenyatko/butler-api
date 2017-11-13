from django.conf.urls import url
from . import views as local_view

urlpatterns = [
    url(r'^users/$', local_view.UserListView.as_view()),
    url(r'^users/(?P<username>\S+)/$', local_view.UserDetailView.as_view()),
    url(r'^devices/$', local_view.DeviceListView.as_view()),
    url(r'^devices/(?P<username>\S+)/$', local_view.DeviceDetailView.as_view()),
    url(r'^token/$', local_view.GetAuthTokenView.as_view()),
    url(r'^token-jwt/$', local_view.GetJwtView.as_view()),
    url(r'^enable/$', local_view.EnableAuthView.as_view()),
    url(r'^mqtt/user/check/$', local_view.CheckMqttUserView.as_view()),
    url(r'^mqtt/superuser/check/$', local_view.CheckMqttSuperuserView.as_view()),
    url(r'^mqtt/acl/check/$', local_view.CheckMqttAclView.as_view()),
]
