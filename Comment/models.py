from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from Users.models import UserInfo
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.


class CommentManager(models.Manager):
    def all(self):
        return super().filter(parent=None)

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super().filter(content_type=content_type,
                            object_id=obj_id).filter(parent=None)
        return qs


class Comment(MPTTModel):
    user = models.ForeignKey(User)
    content = models.TextField()
    create_date = models.DateField(auto_now=True)
    # parent = models.ForeignKey("self", blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # objects = CommentManager()

    def __str__(self):
        return self.content

    def children_comment(self):
        return Comment.objects.filter(parent=self)

    def get_user_info(self):
        return UserInfo.objects.filter(user=self.user)
