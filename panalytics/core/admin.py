from django.contrib import admin

from .models import PageView, Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'tid', 'created_at')


class PageViewAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'project', 'url', 'title', 'referer',
                    'unique_visit')


admin.site.register(Project, ProjectAdmin)
admin.site.register(PageView, PageViewAdmin)
