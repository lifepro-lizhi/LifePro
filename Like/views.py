from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Like
from Blog.models import Blog

# Create your views here.


def ClickLikeButton(request, pk):
    blog = Blog.objects.get(id=pk)

    if not request.user.is_authenticated:
        messages.success(request, 'Your password was updated successfully!')

    else:
        if blog:
            like_exist = Like.objects.filter(object_id=blog.id).\
                         filter(user=request.user)
            if like_exist.count() != 0:
                messages.success(request, '您已经点过赞啦！')
            else:
                like = Like()
                content_type = ContentType.objects.get_for_model(Blog)
                like.content_type = content_type
                like.object_id = blog.pk
                like.user = request.user

                try:
                    like.save()
                except:
                    messages.success(request, '服务器出了点小问题...')
                else:
                    messages.success(request, '点赞并收藏成功！')

    return redirect(reverse('blog:blog_detail', kwargs={'pk': pk}))
