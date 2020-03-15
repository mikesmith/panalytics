from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import PageView, Project


class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
            [field.name for field in obj._meta.fields] + \
            [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'tid', 'created_at')


class PageViewAdmin(ReadOnlyAdmin):
    list_display = ('timestamp', 'project_link', 'url', 'title', 'referer',
                    'unique_visit')

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:core_project_change", args=(obj.project.pk,)),
            obj.project.name
        ))
    project_link.short_description = 'project'


admin.site.register(Project, ProjectAdmin)
admin.site.register(PageView, PageViewAdmin)
