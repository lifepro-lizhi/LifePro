from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from Users.models import UserInfo

# Create your models here.


class LikeManager(models.Manager):
    # def filter_by_blog(self, ):
    #     content_type = ContentType.objects.get_for_model(Blog)
    #     qs = super().filter(content_type=content_type,
    #                         object_id=blog_id)
    #     return qs

    def filter_by_user(self, user_id):
        content_type = ContentType.objects.get_for_model(User)
        qs = super().filter(content_type=content_type,
                            object_id=user_id)
        return qs


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # objects = CommentManager()

    def __str__(self):
        return self.content

    def get_user_info(self):
        return UserInfo.objects.filter(user=self.user)
