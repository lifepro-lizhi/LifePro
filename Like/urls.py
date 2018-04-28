from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'like'
urlpatterns = [
    url(r'^addbloglike/(?P<pk>[0-9]+)/$', views.ClickLikeButton, name = 'click_like_button'),
]
