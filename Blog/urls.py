from django.conf.urls import url
# from django.views.decorators.http import require_POST
from . import views


app_name = 'blog'
urlpatterns = [
    # 创建Blog
    url(r'^blogcreate/$', views.BlogCreateView.as_view(), name='blog_create'),

    # 已发布的Blog的列表、详细、更新、删除
    url(r'^bloglist/$', views.BlogListView.as_view(), name='blog_list'),
    url(r'^categorybloglist/(?P<category>\w+)/$', views.CategoryBlogListView.as_view(), name='category_blog_list'),
    url(r'^blogdetail/(?P<pk>[0-9]+)/$', views.BlogDetailView.as_view(), name='blog_detail'),
    # url(r'^comment_form/$', require_POST(views.CommentFormView.as_view()), name='comment_form_post'),
    url(r'^blogupdate/(?P<pk>[0-9]+)/$', views.BlogUpdateView.as_view(), name='blog_update'),
    url(r'^blogdelete/(?P<pk>[0-9]+)/$', views.BlogDeleteView.as_view(), name='blog_delete'),

    # 还没发布的Blog草稿的列表、详细、删除（更新没有必要）
    url(r'^draftlist/$', views.DraftListView.as_view(), name='draft_list'),
    url(r'^draftdetail/(?P<pk>[0-9]+)/$', views.DraftDetailView.as_view(), name='draft_detail'),
    url(r'^draftupdate/(?P<pk>[0-9]+)/$', views.DraftUpdateView.as_view(), name='draft_update'),
    url(r'^draftdelete/(?P<pk>[0-9]+)/$', views.DraftDeleteView.as_view(), name='draft_delete'),
    url(r'^draftpublish/(?P<pk>[0-9]+)/$', views.publish, name='publish'),

    # 关键字搜索的Blog列表
    url(r'^searchbloglist/$', views.SearchBlogListView.as_view(), name='search_blog_list'),

    # Tutorials页面
    url(r'^tutorialspage/$', views.TutorialsView, name='tutorials_view'),

    # 个人Profile
    url(r'^selfprofile/$', views.ProfileDetailView, name='profile_view'),


]
