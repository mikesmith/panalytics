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
    list_display = ('name', 'tid', 'unique_view_count', 'view_count',
                    'single_day_view_count', 'seven_day_view_count',
                    'thirty_day_view_count', 'top_path')

    def single_day_view_count(self, obj):
        return obj.view_count(days=1)
    single_day_view_count.short_description = '24 Hours'

    def seven_day_view_count(self, obj):
        return obj.view_count(days=7)
    seven_day_view_count.short_description = '7 Days'

    def thirty_day_view_count(self, obj):
        return obj.view_count(days=30)
    thirty_day_view_count.short_description = '30 Days'

    def top_path(self, obj):
        path, count = obj.top_path()
        return f'{count} - "{path}"'
    top_path.short_description = 'Most Visited (C-P)'


class PageViewAdmin(ReadOnlyAdmin):
    list_filter = ('project',)
    list_display = ('timestamp', 'project_link', 'url', 'title', 'referer',
                    'unique_visit',)

    def project_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:core_project_change", args=(obj.project.pk,)),
            obj.project.name
        ))
    project_link.short_description = 'project'


admin.site.register(Project, ProjectAdmin)
admin.site.register(PageView, PageViewAdmin)
