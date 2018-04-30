from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.contenttypes.models import ContentType
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView, TemplateView)
from django.contrib import messages
from Blog.models import Blog
from .models import Comment
from .forms import CommentForm
from Users.models import UserInfo
import time
from datetime import datetime

# Create your views here.

# def comment_interval(comment_create_func):
#     def wrapper(*args):
#         if last_comment_time is None:
#             comment_create_func(*args)
#             last_comment_time = time.time()
#         else:
#             now = time.time()
#             if now - last_comment_time < 60 * 3:
#                 comment_create_func(*args)
#                 last_comment_time = time.time()
#             else:
#                 messages.success(request, '评论太快')


# 创建Comment
def CommentCreate(request, pk):
    user_info = UserInfo.objects.get(user=request.user)
    # 上一次评论的时间与现在时间的差值
    interval = timezone.localtime(timezone.now()) - user_info.last_comment_datetime
    # 如果是第一次评论，或者评论间隔已经大于5分钟，则可以评论
    # print("last: {}".format(user_info.last_comment_datetime))
    # print("now: {}".format(timezone.now()))
    # print("interval: {}".format(interval.total_seconds()))
    if interval.total_seconds() > 60 * 5:
        blog = get_object_or_404(Blog, pk=pk)
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = Comment()
                comment.user = request.user
                comment.content = form.cleaned_data['content']
                comment.create_date = timezone.localtime(timezone.now())

                content_type = ContentType.objects.get_for_model(Blog)
                comment.content_type = content_type
                comment.object_id = blog.pk

                parent_id = request.POST.get('parent_id')
                if parent_id is not None:
                    parent_comment = Comment.objects.filter(id=parent_id)
                    if parent_comment.exists():
                        comment.parent = parent_comment.first()
                    else:
                        comment.parent = None
                else:
                    comment.parent = None

                try:
                    comment.save()
                except:
                    messages.success(request, '评论提交失败！')
                else:
                    messages.success(request, '评论提交成功！')

                user_info.last_comment_datetime = timezone.localtime(timezone.now())
                user_info.save(update_fields=['last_comment_datetime'])

                return redirect(reverse('blog:blog_detail', kwargs={'pk': pk, }))
    # 如果距离上一次评论时间小于5分钟，则不能评论
    elif interval.total_seconds() < 60 * 5:
        messages.success(request, '您评论太快啦~喝口水休息一下吧')
        return redirect(reverse('blog:blog_detail', kwargs={'pk': pk, }))


class CommentDeleteView(DeleteView):
    model = Comment
    success_url = reverse_lazy('blog:blog_list')
    context_object_name = 'comment'
    template_name = "Blog/comment_confirm_delete.html"


def show_genres(request):
    return render(request, "Blog/qqq.html", {'comment': Comment.objects.all()})
