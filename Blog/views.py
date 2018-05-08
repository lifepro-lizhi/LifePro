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
from ipware import get_client_ip
from datetime import timedelta


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
            if blog_info['id'] == 0:
                continue
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
        # 获得IP地址
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        reading_info.ip = ip
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
        reading_info.time = timezone.localtime(timezone.now()) + timedelta(days=0, hours=8)

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


def ProfileDetailView(request):
    profile_chinese = '''
嗨，大家好，欢迎光临我的小站*LifePro*。我叫李智，是一名软件工程师，毕业于武汉一所985高校的通信工程专业，技术狂热范，学习爱好者，Mac重度用户，主机游戏迷。参加工作多年以来，在大厂里当过螺丝钉，在小企业里做过技术经理，也创过业，在创业公司担任过CTO，一直以来都是走的技术路线，忙碌并快乐着。执着于技术，常常觉得编程给自己带来的快乐比玩儿游戏都多。从事过研发的领域比较广，做过网络协议，搞过嵌入式开发，折腾过游戏引擎，玩儿过OpenGL，研究过Web框架和数据库，现在专注的领域为机器学习和计算机视觉，并且坚定以此为以后自己发展和努力的方向。

以前一直以为做技术能给自己带来编码的快乐和可观的收入就足够了，但是在步入而立之年以后，我发现自己在技术领域并没有留下什么实质性的影响力，并且发现了自己关于学习方法方面的一些问题。在工作之余，我在不断学习着其他领域的知识，但是随着时间的迁移，我发现这些技能并没有随着时间的累积而有非常大的提升，也就是说没有达到称得上算是专业的程度。自学生时代起就学习日语和练习吉他，工作之后也学过绘画和摄影，为了学习木雕买过很多书籍和很专业的设备，钢琴也购置了四五年，断断续续的练习着，也曾将经济学作为自己的第二研究领域。但是多年以来，这些技能并没有得到很深入的发展，并没有达到自己期望的专业程度。经过反思，找到了自己在技能学习上一个很大的缺点---没有系统性的专业化训练。为了改正这个缺点，想了很多，最终找到了最适合自己的方法---写作。通过写作，我可以不断的将自己所学过的知识进行输出，不断的将自己所掌握的知识讲述给别人听，而这个持续输出的过程也是对自己头脑中知识网络的整理、归纳和强化，并且他人可以从自己的文章中获得不同程度的提高，也是对自己写作的一种肯定。知识掌握的过程中最难的不是自己弄明白，而是弄明白之后还要能清楚的教授给别人。现在我坚信着一句古训：The best way to Learn is to Teach。

在自己的而立之年，学习不再是一种负担，也不是一种用来赚钱的手段，而是在不断提升自己的过程中寻求满足和快乐的一种方式。做技术同样也是如此，在而立之年这个年纪，做技术并不完全是为了金钱，更重要的是一份坚持的态度，分享的快乐，和不断学习的满足感。自己很崇敬和尊重的翻译大师许渊冲，快100岁高龄了还在不停的写作、翻译和学习，坚持做自己热爱的事情并坚持了一辈子。许老曾说过，对自己热爱的事业，要**尽其所能，得其所好**。我想这也是我们年轻人应该追求的学习和生活态度。

为此我做了这个网站，用来通过写作输出各种教程，一来让自己学习过的技能更加专业和系统，二来给自己不断增加学习的动力，而且可以尽自己的一点微薄之力帮助到一些需要成长的人。现在我几乎每天早晨6点起来写作，工作之余的大部分业余时间都用来写作和学习新领域的知识。短期和长期内计划增加的写作领域还有网络协议、计算机视觉、C/C++、UNIX、OpenGL、Unity、STM32、TensorFlow、音乐理论、经济学、法语、摄影、厨艺、主机游戏评测等等。虽然跨度很广，领域也很多，但是我相信只要努力不断学习，坚持写作，终会能够做到在不同领域进行持续不断的输出。

希望通过写作，能遇到更好、更专业的自己，也期待能认识到更多的朋友。

Life is more Professional than yesterday。
'''

    profile_english = '''
Hi,welcome to my *LifePro* site.My name is Li Zhi,a software programmer,a geeker,a learning fan,a Mac fanatical user,and a severe TV gamer.Graduated from the major of communication engineering at a 985 university in Wuhan,China.From the years since started work,I've been an employee in big company,a technical manager in small private enterprise,and been CTO in a start-up company.All these years I've been concentrating on technology fields,work hard but most importantly feel happy at the mean time.I love coding,quite a few times I feel like doing the coding is more interseting than playing video games.And I've been wrting programs in quite a few fields using different kinds of languages,including network protocols,embeded system,game engine,OpenGL,Django Web framework and PostgreSQL database.Nowadays I put all my focus in machine learning and computer vision,and insist this is the working field that will last in my future.

All these years I think do the coding is just for fun and money.That's it,nothing more.But when I step into my 30's,I realize that I haven't left any impressive influence in any tech field,and I've found some really serious problems in my study methods.I have been learning knowledge in different kinds of fields during my spare time after work,but as the time flying by,I didn't feel some very big impressive improvment in these areas,not even talk about been professional.I've been studying Japanese and playing guitar since college time,and have learned drawing and photographing during my work days,and in order to learn wooden craft I even bought many books and professionl tools.Piano have been put in my room for about 4 or 5 years,but not get continuous training.At the same time,I read ecnomics books and consider it as my secondary research field.But years have been passed,I'm still far away from being professional in those subjects.

In order to get rid of the current situation,I've done a lot of think,and finaly I found the most principal reason---not been taking systematic and professional training.Mostly the same time I've found the most efficient way of how to sovle that---by writing.Through writing,I can take the knowledge in my head into continuous outputs,and let these continuous outputs become a way of teaching.These whole stpes also is a way of orgnizing, generalizing and enhancing the knowledge that I've learned.Meantime,it's also an honor that other people who needs help can take some pratical advice from my blogs.The most hard part of completely mastering the knowledge of one field is not the understanding by yourself,but the teaching and letting others to grasp the key point by your own words.So now I believe in the well-known old Latin principle Docendo discimus---"The best way to Learn is to Teach".

Under my 30's,studying is not a burden,not even a way of making money,but a way of satisfying and entertaining by improving myself.The same reason for writing code,it's an attitude of persistence,a happiness of sharing,and a way of satisfying by learning.The famous translator Xu Yuanchong,whom I respect and esteem very much is still constantly writing,translating and learning even near his 100's.He once said that to treat the things that we love to do,we must **do our best,get we want most**.I think this is the real attitude of facing life and studying at the best age like us.

So I build up this website,outputting all kinds of tutorials that I've learned by writing blogs.First,this can help me getting more systematic and professional trainings.Second,this can help me gaining constantly motivation for learning new things.Moreover,it's an honor for me to do some little job to help those who needs help for their level improvment.Nowadays I almost wake up 6:00 AM every morning to start writing,and spend most of my spare time on writing and learning.The short and long term of writing schedule including network protocol,computer vision,C/C++,UNIX,OpenGL,Unity,STM32,TensorFlow,musical theory，ecnomics,French,photographing,cooking and TV game reviews,etc.Although these are lots of work,but as long as I writing hard and learning diligently,I believe I can eventually keep continuous outputs on different kinds of subjects.

Hopefully,I expect to build up a better and more professional myself by writing,and I'd love to make more and more friends through this little website.

Thanks again for visiting my site :-)

Life is more Professional than yesterday.
    '''

    profile_japanese = '''
こんにちは、私のLifeProサイトへようこそ！私の名前はりちで、ソフトウェアエンジニアです。通信エンジニアリング専攻で、武漢の985大学を卒業した。技術ファン、学習愛好家、Macのヘビーユーザー、コンソールゲームのファンを抱えています。長年勤務以来、大手のスクリューとして、中小企業のテクニカルマネージャーとして、スタートアップ企業のCTOとしても働いていました。テクノロジの道を歩いていると、懸命に働いた時に楽を感じている。テクノロジーに従うと、コンソールゲームをするよりプログラミングが私にとって楽しいと感じることがよくあります。研究開発の領域は多いのは、ネットワークプロトコル、組み込み開発、ゲームエンジン、OpenGL、Django Webフレームワークとデータベースの研究を含んでいる。今は機械学習とコンピュータビジョンに焦点を当てています。これは将来の自己開発と勤勉の方向と思います。

以前に、私は技術を使ってプログラミングをするに幸福と利益をもたらすと思っていましたが、今年私の30歳に入り込んた後、技術分野に大きな影響を与えずに見えませんでした。同時に学習方法に関する自身の質問はあります。暇な時間には、私は他の知識分野についても常に学んでいますが、時間が経つにつれて、これらのスキルは時間が経つにつれて改善されない、つまりプロとしてはみなされていません。私は学生時代から日本語を学んだり、ギターを練習したり、仕事の後で絵画や写真撮影も学びました。木彫りを学ぶために、たくさんの本やプロの機器を買いました。ピアノは5年間も購入されており、断続的に演奏されています。さらに経済学を第二の研究領域にするために、たくさんの本も読んでいます。

しかし、長年にわたり、これらのスキルは深く発展せず、期待されたのプロフェッショナリズムのレベルに達していません。再考した後、私はスキル学習に大きな不利をもたらしましたーーー体系的な専門訓練はありません。この欠点を解消するために、私はたくさんを考えて、最終的には自分にとって最適な方法を見つけましたーーー執筆ことだ。執筆を通して、私の学んだものを引き続き輸出し、その輸出について他人に絶えず伝えることができます。 そんなの過程に私は誘導的で激化しているものもあれば、自分の記事からさまざまな人のレベルの改善を得ることもできますし、自分の文章を肯定するものでもあります。知識習得の過程で最も難しいのことは自分自身で理解するのではなく、それをはっきりと理解し、自身の言葉を使いて他人に教えることです。今私は古代の教訓を信じている：学ぶに最も良い方法は教えることです。

自分の３０歳に、学習はもはや負担ではなく、さらにお金を稼ぐ手段でもなく、常に自分自身を改善する過程で満足と幸福を求める方法です。同じことで、テクノロジーはお金のためだけではなく、永続的な態度、幸福の共有、そして継続的な学習の満足度が重要です。許淵衝、私は尊重する翻訳者、100歳も近いにまだ執筆、翻訳、学習しています。彼は愛しすることを強く続けているます。彼はかつて、愛していることに最善を尽くし、自分が望むものを手に入ればと言った。それは私みたいの若者が追求すべき学習と人生の態度でもあると思います。

この目的のために、私はこのウェブサイトを作成した、さまざまなチュートリアルを出力します。まずは専門的体系的に学んだスキルを身に付けさせて、次に学習のモチベーションを高めももらえます。さらに、成長するに必要な建議が欲しいの人々に助けてくれることに楽を感じます。今私はほとんど毎朝6時に起きて執筆します。空き時間のほとん執筆をして、新しい知識を学んでいます。短期および長期の執筆の計画に、ネットワークプロトコル、コンピュータビジョン、C/C++、UNIX、OpenGL、Unity、STM32、TensorFlow、音楽理論、経済学、フランス語、写真、料理、コンソールゲーム評価などを含んでいる。分野と範囲が多いのですが、私は引き続き学び、執筆し続けると、最終的には異なる分野で継続的な成果を達成することができます。

私は執筆を通して、自分をより良く、よりプロな自身に出会えることを願っています。もっと多くの友達を見ることも楽しみにしています。

Life is more Professional than yesterday。
'''

    profile_content = markdown.Markdown(extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite',
                                         # 'markdown.extensions.toc',
                                         TocExtension(slugify=slugify),
                                     ])
    context = {'profile_content_chinese': profile_content.convert(profile_chinese),
               'profile_content_english': profile_content.convert(profile_english),
               'profile_content_japanese': profile_content.convert(profile_japanese),
              }

    reading_info = ReadingInfo()
    # 获得IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    reading_info.ip = ip
    # 如果用户已经登录，则reading_info中的user为当前登录用户；否则为默认的NotLoginUser
    if request.user.is_authenticated:
        reading_info.username = request.user.username

    # 如果当前用户已经登录，保存是否点赞信息
    reading_info.did_like = False

    # 如果当前用户已经登录，则在reading_info中保存当前用户对该文章的评论数
    reading_info.user_comment_count = 0

    reading_info.content_type = ContentType.objects.get_for_model(Blog)
    reading_info.object_id = 0
    reading_info.blog_name = "Profile"
    reading_info.time = timezone.localtime(timezone.now()) + timedelta(days=0, hours=8)

    reading_info.save()
    # END: 文章阅读信息统计

    return render(request, 'Blog/profile.html', context)
