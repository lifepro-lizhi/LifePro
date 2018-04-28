from django.conf.urls import url
from . import views


app_name = 'users'
urlpatterns = [
    url(r'^register/$', views.UserRegister, name='register'),
    # url(r'^login/$', views.UserLoginView.as_view(), name='login_test'),
    url(r'^login/$', views.UserLogin, name='user_login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='user_logout'),
    url(r'^userprofile/(?P<pk>[0-9]+)/$', views.UserProfileView.as_view(), name='user_profile'),
    url(r'^userprofileupdate/$', views.UserUpdateView, name='user_profile_update'),
]
