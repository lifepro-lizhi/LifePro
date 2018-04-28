from django.conf.urls import url
# from django.views.decorators.http import require_POST
from . import views


app_name = 'comment'
urlpatterns = [
    url(r'^createcomment/(?P<pk>[0-9]+)/$', views.CommentCreate, name='create_comment'),
    url(r'^show/$', views.show_genres, name='create_comment'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.CommentDeleteView.as_view(), name='delete_comment'),
]
