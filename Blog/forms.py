from django import forms
from .models import Blog, Comment
# from pagedown.widgets import PagedownWidget


class BlogCreateForm(forms.ModelForm):
    # for pagedown
    # content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = Blog
        fields = ('title', 'content')


class BlogPublishForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('category', 'cover_image', 'cover_breif', 'is_series',
                  'series_keyword', 'series_index')
