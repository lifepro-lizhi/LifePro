from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class ReadingInfo(models.Model):
    username = models.CharField(max_length=255, default="NotLoginUser")
    time = models.DateTimeField(auto_now=True)
    blog_name = models.CharField(max_length=255, default="")
    did_like = models.BooleanField(default=False)
    user_comment_count = models.IntegerField(default=0)
    ip = models.CharField(max_length=255, null=True)
    # blog = models.ForeignKey(Blog, related_name='reading_info',
    #                          on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'ReadingInfo'
