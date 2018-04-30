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
    publish_date = forms.DateField(widget=forms.DateInput(attrs={'class':'timepicker'}))
    class Meta:
        model = Blog
        fields = ('publish_date', 'category', 'cover_image_url', 'cover_breif', 'is_series',
                  'series_keyword', 'series_index')
