from django.shortcuts import render, redirect
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView, TemplateView)
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import (LoginView, LogoutView)
from django.urls import reverse_lazy, reverse
from .models import UserInfo
from .forms import UserForm, UserInfoForm, UserLoginForm
from Like.models import Like
from Blog.models import Blog
from django.db import IntegrityError


# Create your views here.


# class UserRegisterView(CreateView):
#     model = UserInfo
#     template_name = 'users/register.html'
#     form_class = RegisterForm()
#     success_url = reverse_lazy('blog:bloglist')

# def UserRegister(request):
#     if request.method == 'POST':
#         user_form = UserForm(request.POST)
#         userinfo_form = UserInfoForm(request.POST, request.FILES)
#         if user_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()

#             userinfo = userinfo_form.save(commit=False)
#             userinfo.user = user
#             userinfo.save()
#
#             return redirect(reverse('blog:blog_list'))
#         else:
#             print('form invalid')
#     else:
#         user_form = UserForm()
#         userinfo_form = UserInfoForm()
#         context = {'user_form': user_form, 'userinfo_form': userinfo_form}
#         return render(request, 'Users/register.html', context)

def UserRegister(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # 如果用户名、密码和Email为空，则注册失败
        if username == '' or password == '' or email == '':
            context = {'error': 'empty_input'}
            return render(request, 'Users/register_failed.html', context)

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            context = {'error': 'same_email'}
            return render(request, 'Users/register_failed.html', context)

        user = User(username=username, password=password, email=email)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            context = {'error': 'same_id'}
            return render(request, 'Users/register_failed.html', context)

        # 检查用户是否上传头像，如果没有上传则将portrain置为None，以后用系统默认头像
        if not bool(request.FILES):
            portrait = "Blog/portraits/user_icon.png"
        else:
            portrait = request.FILES['portrait']

        userinfo = UserInfo(user=user, portrait=portrait)
        userinfo.save()

        login_user = authenticate(username=username, password=password)
        login(request, login_user)

        return redirect(reverse('blog:blog_list'))


def UserLogin(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # 登录之后返回上一次访问的网页
            last_page_url = request.META.get('HTTP_REFERER')
            return redirect(last_page_url)
        else:
            return render(request, 'Users/login_failed.html')


class UserLoginView(LoginView):
    template_name = 'Users/login.html'
    # form_class = UserLoginForm


class UserLogoutView(LogoutView):
    # logout之后返回上一次访问的网页
    def get_next_page(self):
        last_page_url = self.request.META.get('HTTP_REFERER')
        # 如果在个人页面点击logout，则之后要返回主页，否则会再次回到个人页面，这时会因为user信息丢失而出现错误
        # 如果是其它情况，则返回上一次访问的网页
        if 'userprofile' in last_page_url:
            return reverse('blog:blog_list')
        else:
            return last_page_url


class UserProfileView(DetailView):
    model = UserInfo
    context_object_name = 'user_info'
    template_name = 'Users/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 获取当前用户点赞的文章
        user_likes = Like.objects.filter(user=self.request.user)
        liked_blogs = []
        for like in user_likes:
            blog = Blog.objects.get(id=like.object_id)
            liked_blogs.append(blog)

        context['liked_blogs'] = liked_blogs
        context['liked_blogs_count'] = len(liked_blogs)

        return context


def UserUpdateView(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        password = request.POST['password']
        email = request.POST['email']

        # 如果用户名、密码和Email为空，则注册失败
        if password == '' or email == '':
            context = {'error': 'empty_input'}
            return render(request, 'Users/register_failed.html', context)

        user.password = password
        user.set_password(password)
        user.email = email
        try:
            user.save()
        except IntegrityError:
            context = {'error': 'same_id'}
            return render(request, 'Users/register_failed.html', context)

        # 检查用户是否上传头像，如果没有上传则将portrain置为None，以后用系统默认头像
        if not bool(request.FILES):
            portrait = ""
        else:
            portrait = request.FILES['portrait']

        userinfo = user.userinfo
        userinfo.portrait = portrait
        userinfo.save()

        login_user = authenticate(username=user.username, password=password)
        login(request, login_user)

        return redirect(reverse('blog:blog_list'))
    else:
        user = User.objects.get(id=request.user.id)
        user_info = user.userinfo
        context = {'user': user, 'user_info': user_info}
        return render(request, 'Users/user_info_update.html', context)
