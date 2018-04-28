from django.contrib import admin
from .models import Blog

# Register your models here.


class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'publish_date', 'category', 'id']
    search_fields = ['content']

    class Meta:
        model = Blog


admin.site.register(Blog, BlogAdmin)
