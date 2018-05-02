from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView, TemplateView)
from .models import Blog
from Comment.models import Comment
from Users.models import UserInfo
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import BlogCreateForm, BlogPublishForm
from Comment.forms import CommentForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormMixin, FormView
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from Like.models import Like
from ReadingInfo.models import ReadingInfo
from . import category
import markdown
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension


# Create your views here.

class BlogListView(ListView):
    model = Blog
    template_name = 'Blog/blog_list.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        return Blog.objects.filter(draft__exact=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # START 分页器
        paginator = Paginator(self.get_queryset().order_by('-publish_date'), 5)

        page = self.request.GET.get('page')
        try:
            blogs_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blogs_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),deliver last page of results.
            blogs_page = paginator.page(paginator.num_pages)

        context['blogs_page'] = blogs_page
        # END 分页器

        # START 侧边栏Read Top 10
        top_reading_list = []
        top_reading_queryset = ReadingInfo.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_reading_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_reading_list.append(blog_info)

        context['top_reading_list'] = top_reading_list
        # END 侧边栏Read Top 10

        # START 侧边栏Comment Top 10
        top_comment_list = []
        top_comment_queryset = Comment.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_comment_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_comment_list.append(blog_info)

        context['top_comment_list'] = top_comment_list
        # END 侧边栏Read Top 10

        # START 侧边栏Like Top 10
        top_like_list = []
        top_like_queryset = Like.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_like_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_like_list.append(blog_info)

        context['top_like_list'] = top_like_list
        # END 侧边栏Like Top 10

        # START 侧边栏Recent Post
        recent_post_list = []
        recent_post_queryset = Blog.objects.all().order_by('-publish_date')[0:5]
        for each in recent_post_queryset:
            recent_post_list.append(each)

        context['recent_post_list'] = recent_post_list
        # END 侧边栏Recent Post

        context['up_to_current_page_list'] = blogs_page.paginator.page_range[0:(blogs_page.number + 1)]

        return context

    class Meta:
        ordering = ('-publish_date')


class CategoryBlogListView(ListView):
    model = Blog
    template_name = 'Blog/blog_list.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        return Blog.objects.filter(draft__exact=False).\
                                   filter(category__exact=self.kwargs['category'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.get_queryset().order_by('-publish_date'), 5)

        page = self.request.GET.get('page')
        try:
            blogs_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blogs_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),deliver last page of results.
            blogs_page = paginator.page(paginator.num_pages)

        # START 侧边栏Read Top 10
        top_reading_list = []
        top_reading_queryset = ReadingInfo.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_reading_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_reading_list.append(blog_info)
        # END 侧边栏Read Top 10

        # START 侧边栏Comment Top 10
        top_comment_list = []
        top_comment_queryset = Comment.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_comment_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_comment_list.append(blog_info)
        # END 侧边栏Read Top 10

        # START 侧边栏Recent Post
        recent_post_list = []
        recent_post_queryset = Blog.objects.all().order_by('-publish_date')[0:5]
        for each in recent_post_queryset:
            recent_post_list.append(each)
        # END 侧边栏Recent Post

        context['blogs_page'] = blogs_page
        context['up_to_current_page_list'] = blogs_page.paginator.page_range[0:(blogs_page.number + 1)]
        context['top_reading_list'] = top_reading_list
        context['top_comment_list'] = top_comment_list
        context['recent_post_list'] = recent_post_list

        return context

    class Meta:
        ordering = ('publish_date')


# 设置全局变量search_item，为了在网页中进行搜索显示后，切换搜索页面时将刚刚搜索的词条保存在搜索栏中
search_item = ''


class SearchBlogListView(ListView):
    model = Blog
    template_name = 'Blog/blog_list.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        global search_item
        print()
        print("before: {}".format(search_item))
        search_content = self.request.GET.get('q')

        # 在切换搜索下一面时，此时的self.request.GET.get('q')为None，因此这里将搜索的词条保存在全局变量search_item中
        if search_content is not None:
            search_item = search_content
            print("is not None ++++++++++++".format(search_content))
        else:
            print("is None ------------ {}".format(search_content))
        print("************* {}".format(search_item))
        return Blog.objects.filter(draft__exact=False).filter(Q(title__icontains=search_item) | Q(content__icontains=search_item))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # search_content = self.request.GET.get('q')
        # blog_list = Blog.objects.filter(draft__exact=False).filter(Q(title__icontains=search_content) | Q(content__icontains=search_content)).order_by('publish_date')

        paginator = Paginator(self.get_queryset().order_by('-publish_date'), 5)

        page = self.request.GET.get('page')
        try:
            blogs_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blogs_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),deliver last page of results.
            blogs_page = paginator.page(paginator.num_pages)

        context['blogs_page'] = blogs_page

        # START 侧边栏Read Top 10
        top_reading_list = []
        top_reading_queryset = ReadingInfo.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_reading_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_reading_list.append(blog_info)
        # END 侧边栏Read Top 10

        # START 侧边栏Comment Top 10
        top_comment_list = []
        top_comment_queryset = Comment.objects.values('object_id').\
                                       annotate(count=Count('object_id')).\
                                       order_by('-count')[0:10]
        for each in top_comment_queryset:
            blog_info = {}
            blog_info['id'] = each['object_id']
            blog_info['count'] = each['count']
            blog_info['title'] = Blog.objects.get(id=each['object_id']).title
            top_comment_list.append(blog_info)
        # END 侧边栏Read Top 10

        # START 侧边栏Recent Post
        recent_post_list = []
        recent_post_queryset = Blog.objects.all().order_by('-publish_date')[0:5]
        for each in recent_post_queryset:
            recent_post_list.append(each)
        # END 侧边栏Recent Post

        context['up_to_current_page_list'] = blogs_page.paginator.page_range[0:(blogs_page.number + 1)]
        context['top_reading_list'] = top_reading_list
        context['top_comment_list'] = top_comment_list
        context['recent_post_list'] = recent_post_list
        # 将网页中搜索栏的内容置位search_item
        context['search_item'] = search_item

        return context


class BlogCreateView(UserPassesTestMixin, CreateView):
    model = Blog
    form_class = BlogCreateForm
    template_name = 'Blog/blog_create.html'
    # fields = ('blog_title', 'blog_content')
    success_url = reverse_lazy('blog:draft_list')

    def test_func(self):
        return self.request.user.is_superuser


def publish(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogPublishForm(request.POST)
        if form.is_valid():
            blog.category = form.cleaned_data["category"]
            blog.cover_image_url = form.cleaned_data["cover_image_url"]
            blog.cover_breif = form.cleaned_data["cover_breif"]
            blog.publish_date = form.cleaned_data['publish_date']
            blog.is_series = form.cleaned_data['is_series']
            blog.series_keyword = form.cleaned_data['series_keyword']
            blog.series_index = form.cleaned_data['series_index']
            blog.draft = False
            blog.save()

            # return reverse_lazy("blog:blog_detail", kwargs={'pk': blog.pk})
            return redirect(reverse("blog:blog_detail", kwargs={'pk': pk}))
    else:
        if blog.draft is True:
            publish_form = BlogPublishForm()
            context = {"publish_form": publish_form, }
            return render(request, 'Blog/blog_publish.html', context)


# class CommentFormView(FormView):
#     form_class = CommentForm
#     success_url = reverse_lazy('blog:blog_detail')
#     template_name = 'blog/blog_comment_form.html'


class BlogDetailView(FormMixin, DetailView):
    model = Blog
    context_object_name = 'blog'
    # template_name = 'Blog/blog_detail.html'
    template_name = 'Blog/blog_sidebar_base.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        print(">>>>>>>> ip: {}".format(ip))

        instance = Blog.objects.get(id=self.kwargs['pk'])
        # comments = Comment.objects.filter_by_instance(instance)
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Blog),
                                          object_id=instance.id)

        comment_form = CommentForm()

        if self.request.user.is_authenticated:
            user_info = UserInfo.objects.filter(user=self.request.user).first()
        else:
            user_info = None

        # if instance.is_series:
        #     self.template_name = 'Blog/blog_detail_series.html'

        # START: Blog正文Markdown
        blog_content = markdown.Markdown(extensions=[
                                             'markdown.extensions.extra',
                                             'markdown.extensions.codehilite',
                                             # 'markdown.extensions.toc',
                                             TocExtension(slugify=slugify),
                                         ])
        context['blog_content'] = blog_content.convert(instance.content)
        # 目录
        context['toc'] = blog_content.toc
        # END: Blog正文Markdown

        # 判断这篇文章是否被赞过，如果被赞过，则网页上显示红色按钮；如果没有，则页面上显示白色按钮
        # 如果用户没有登录，则直接显示白色按钮
        if not self.request.user.is_authenticated:
            already_like = False
        # 如果用户已经登录
        else:
            like = Like.objects.filter(content_type=ContentType.objects.get_for_model(Blog),
                                       object_id=instance.id)
            # 首先判断这篇文章是否有赞
            if like.count() != 0:
                # 然后判断当前登录用户是否赞过这篇文章
                try:
                    user_like = like.get(user=self.request.user)
                    if user_like is not None:
                        already_like = True
                    else:
                        already_like = False
                except ObjectDoesNotExist:
                    already_like = False

            # 如果没有赞，则alread_like=False，显示白色按钮
            else:
                already_like = False

        # START: 文章阅读信息统计
        reading_info = ReadingInfo()
        # 如果用户已经登录，则reading_info中的user为当前登录用户；否则为默认的NotLoginUser
        if self.request.user.is_authenticated:
            reading_info.username = self.request.user.username

        # 如果当前用户已经登录，保存是否点赞信息
        reading_info.did_like = already_like

        # 如果当前用户已经登录，则在reading_info中保存当前用户对该文章的评论数
        if self.request.user.is_authenticated:
            comment = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Blog),
                                             object_id=instance.id,
                                             user=self.request.user)
            reading_info.user_comment_count = comment.count()

        reading_info.content_type = ContentType.objects.get_for_model(Blog)
        reading_info.object_id = instance.id
        reading_info.blog_name = instance.title
        reading_info.time = timezone.localtime(timezone.now())

        reading_info.save()
        # END: 文章阅读信息统计

        # START: 系列教程
        # 如果文章是系列教程
        category_dict = []
        if instance.is_series:
            is_series = True
            if instance.series_keyword == 'django_blog':
                category_dict = category.django_blog_category
                context['category_name'] = "Django博客教程"
            elif instance.series_keyword == 'postgresql':
                category_dict = category.postgresql_category
                context['category_name'] = "深入浅出PostgreSQL数据库"
            elif instance.series_keyword == 'mac_tips':
                category_dict = category.mac_tips_category
                context['category_name'] = "Mac实用操作技巧"
            elif instance.series_keyword == 'mac_finder':
                category_dict = category.mac_finder_category
                context['category_name'] = "玩转Mac Finder"
            elif instance.series_keyword == 'mac_alfred':
                category_dict = category.mac_alfred_category
                context['category_name'] = "玩转Mac Alfred"
            elif instance.series_keyword == 'vuforia':
                category_dict = category.vuforia_category
                context['category_name'] = "Vuforia AR开发完全指南"
            elif instance.series_keyword == 'japanese':
                category_dict = category.japanese_category
                context['category_name'] = "日本語文法"

            if str(int(instance.series_index) - 1) in category_dict:
                previous_title = category_dict[str(int(instance.series_index) - 1)]
                try:
                    previous_pk = Blog.objects.get(title__icontains=previous_title).pk
                    context['previous_title'] = previous_title
                    context['previous_pk'] = previous_pk
                except ObjectDoesNotExist:
                    pass

            if str(int(instance.series_index) + 1) in category_dict:
                next_title = category_dict[str(int(instance.series_index) + 1)]
                try:
                    next_pk = Blog.objects.get(title__icontains=next_title).pk
                    context['next_title'] = next_title
                    context['next_pk'] = next_pk
                except ObjectDoesNotExist:
                    pass
        else:
            is_series = False
        # END: 系列教程

        # START: 评论
        # 如果用户评论成功，则comment_success为True，否则为False
        # 这样做的目的是为了当用户提交评论成功后，再次返回文章详情页面时要有评论成功的提示
        if 'comment_success' in self.kwargs:
            if self.kwargs['comment_success'] is True:
                comment_success = True
            else:
                comment_success = False
        else:
            comment_success = False
        # END: 评论

        # START: Sidebar目录
        if instance.is_series:
            is_series = True
            if instance.series_keyword == 'django_blog':
                category_dict = category.django_blog_category
                context['category_name'] = "Django博客教程"
            elif instance.series_keyword == 'postgresql':
                category_dict = category.postgresql_category
                context['category_name'] = "深入浅出PostgreSQL数据库"
            elif instance.series_keyword == 'mac_tips':
                category_dict = category.mac_tips_category
                context['category_name'] = "Mac实用操作技巧"
            elif instance.series_keyword == 'mac_finder':
                category_dict = category.mac_finder_category
                context['category_name'] = "玩转Mac Finder"
            elif instance.series_keyword == 'mac_alfred':
                category_dict = category.mac_alfred_category
                context['category_name'] = "玩转Mac Alfred"
            elif instance.series_keyword == 'vuforia':
                category_dict = category.vuforia_category
                context['category_name'] = "Vuforia AR开发完全指南"
            elif instance.series_keyword == 'japanese':
                category_dict = category.japanese_category
                context['category_name'] = "日本語文法"

            # 目录中的blog名称列表
            category_blog_title_list = category_dict.values()
            # category_blog_title_list = category_dict.items()

            # 目录中的blog pk列表
            category_blog_pk_list = []
            for title in category_blog_title_list:
                try:
                    pk = Blog.objects.get(title=title).pk
                except ObjectDoesNotExist:
                    pk = 0

                category_blog_pk_list.append(pk)
            # 将名称和pk组合成一个(title, pk)的列表，方便在模板中使用
            category_blog_title_pk_list = zip(category_blog_title_list,
                                              category_blog_pk_list)
            context['category_blog_title_pk_list'] = category_blog_title_pk_list
        # END: Sidebar目录

        context['comments'] = comments
        context['comment_form'] = comment_form
        context['user_info'] = user_info
        context['already_like'] = already_like
        context['is_series'] = is_series
        context['comment_success'] = comment_success

        return context

    # def post(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect(reverse('users:login'))
    #     self.object = self.get_object()
    #     form = self.get_form()
    #
    #     blog = Blog.objects.get(id=self.kwargs['pk'])
    #     if form.is_valid():
    #         content_type = ContentType.objects.get_for_model(Blog)
    #         obj_id = self.kwargs['pk']
    #         parent_id = request.POST.get('parent_id')
    #
    #         if parent_id is not None:
    #             parent_qs = Comment.objects.filter(id=parent_id)
    #             if parent_qs.exists():
    #                 parent_obj = parent_qs.first()
    #             else:
    #                 parent_obj = None
    #         else:
    #             parent_obj = None
    #
    #         form.save(commit=False)
    #         comment_new = Comment(user=request.user,
    #                               content_type=content_type,
    #                               object_id=obj_id,
    #                               content=form.cleaned_data.get('content'),
    #                               parent=parent_obj)
    #         comment_new.save()
    #         return redirect(blog)
    #     else:
    #         print('form invalid')
    #         print(form.errors)
    #         return self.form_invalid(form)


class BlogUpdateView(UserPassesTestMixin, UpdateView):
    model = Blog
    context_object_name = 'blog'
    form_class = BlogCreateForm
    template_name_suffix = "_create"
    # success_url = reverse_lazy('blog:blog_detail', kwargs={'pk': object.pk})
    # redirect_field_name = 'blog/blog_detail.html'

    def get_success_url(self):
        return reverse_lazy('blog:blog_detail',
                            kwargs={'pk': self.get_object().id})

    def test_func(self):
        return self.request.user.is_superuser


class BlogDeleteView(UserPassesTestMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')
    context_object_name = 'blog'

    def test_func(self):
        return self.request.user.is_superuser


class DraftListView(ListView):
    model = Blog
    template_name = 'Blog/draft_list.html'
    context_object_name = 'drafts'

    def get_queryset(self):
        # return Blog.objects.filter(draft__exact=True).\
        #                            filter(publish_date__lte=timezone.localtime(timezone.now())).\
        #                            order_by('publish_date')
        return Blog.objects.filter(draft__exact=True)


class DraftDetailView(DetailView):
    model = Blog
    context_object_name = 'draft'
    template_name = 'Blog/draft_detail.html'


class DraftUpdateView(UserPassesTestMixin, UpdateView):
    model = Blog
    context_object_name = 'draft'
    form_class = BlogCreateForm
    template_name = "Blog/blog_create.html"
    # template_name_suffix = "_create"
    # success_url = reverse_lazy('blog:blog_detail', kwargs={'pk': object.pk})
    # redirect_field_name = 'blog/blog_detail.html'

    def get_success_url(self):
        return reverse_lazy('blog:draft_detail',
                            kwargs={'pk': self.get_object().id})

    def test_func(self):
        return self.request.user.is_superuser


class DraftDeleteView(UserPassesTestMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:draft_list')
    context_object_name = 'blog'

    def test_func(self):
        return self.request.user.is_superuser


def TutorialsView(request):
    return render(request, 'Blog/tutorials_page.html')


def test(request):
    return render(request, 'Blog/Series/mac_alfred_series.html')
