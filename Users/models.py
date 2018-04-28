from django.db import models
from django.contrib.auth.models import User

# Create your models here.


def upload_file_name(instance, filename):
    ext = filename.split('.')[-1]
    return 'Blog/portraits/{}-{}.{}'.format(instance.user.id,
                                            instance.user.username,
                                            ext)


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # portrait = models.ImageField(upload_to='Blog/portraits', blank=True)
    portrait = models.ImageField(upload_to=upload_file_name, blank=True)
    last_comment_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
