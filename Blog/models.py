from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from Comment.models import Comment
from Like.models import Like
from ReadingInfo.models import ReadingInfo

# Create your models here.

CATEGORY_CHOICES = (
    ('C', 'C'),
    ('UNIX', 'UNIX'),
    ('Python', 'Python'),
    ('MachineLearning', 'MachineLearning'),
    ('Django', 'Django'),
    ('Math', 'Math'),
    ('Network', 'Network'),
    ('OpenGL', 'OpenGL'),
    ('Unity', 'Unity'),
    ('PostgreSQL', 'PostgreSQL'),
    ('STM32', 'STM32'),
    ('Bootstrap', 'Bootstrap'),
    ('Vim', 'Vim'),
    ('Mac', 'Mac'),
    ('Cooking', 'Cooking'),
    ('ReadingNote', 'ReadingNote'),
    ('Music', 'Music'),
    ('English', 'English'),
    ('Japanese', 'Japanese'),
    ('French', 'French'),
)


def upload_file_name(instance, filename):
    ext = filename.split('.')[-1]
    return 'Blog/blog_covers/{}-{}.{}'.format(instance.id, instance.title, ext)


class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    created_date = models.DateField(auto_now=True)
    publish_date = models.DateField(auto_now=True)

    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255,
                                default='Python')
    cover_image = models.ImageField(upload_to=upload_file_name, blank=True)
    cover_breif = models.TextField(max_length=1500, blank=True)

    draft = models.BooleanField(default=True)

    is_series = models.BooleanField(default=False)
    series_keyword = models.CharField(max_length=100, blank=True)
    series_index = models.IntegerField(null=True)

    comments = GenericRelation(Comment,  related_query_name='blog')
    likes = GenericRelation(Like, related_query_name='blog')
    reading_info = GenericRelation(ReadingInfo, related_query_name='blog')

    def __str__(self):
        return self.title

    def publish(self):
        self.publish_time = timezone.now()
        self.save()

    def get_absolute_url(self):
        if self.draft is True:  # 如果还是草稿，则返回draft_detail
            return reverse('blog:draft_detail', kwargs={'pk': self.pk})
        else:  # 如果已经发布，则返回blog_detail
            return reverse('blog:blog_detail', kwargs={'pk': self.pk})

    # @property
    # def commentss(self):
    #     instance = self
    #     qs = Comment.objects.filter_by_instance(instance)
    #     return qs
