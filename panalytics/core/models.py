from django.db import models
from urllib.parse import urlparse
from django.utils import timezone
from django.db.models import Count
import re

from .utils import get_tracking_id


class Project(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tid = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.tid:
            self.tid = get_tracking_id()
            while Project.objects.filter(tid=self.tid).exists():
                self.tid = get_tracking_id()
        super().save(*args, **kwargs)

    def view_count(self, days=None):
        q = PageView.objects.filter(project=self)
        if days:
            days_ago = timezone.now() - timezone.timedelta(days=days)
            q = q.filter(timestamp__gte=days_ago)
        return q.count()

    def unique_view_count(self, days=None):
        q = PageView.objects.filter(project=self, unique_visit=True)
        if days:
            days_ago = timezone.now() - timezone.timedelta(days=days)
            q = q.filter(timestamp__gte=days_ago)
        return q.count()

    def top_path(self):
        path_values = PageView.objects.filter(project=self.pk).values('path')
        q = path_values.annotate(count=Count('path')).order_by('-count')
        path_list = [(x['path'], x['count']) for x in q]
        return path_list[0]

    @staticmethod
    def is_valid_tracking_id(tid):
        if not tid:
            return False

        if not re.match(r'PA-[A-Z0-9]{9}$', tid):
            return False

        if not Project.objects.filter(tid=tid).exists():
            return False

        return True

    def __str__(self):
        return self.name


class PageView(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='pageviews')
    protocol = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    path = models.CharField(max_length=255, blank=True)
    url = models.TextField()
    title = models.TextField(blank=True)
    window_width = models.PositiveIntegerField()
    window_height = models.PositiveIntegerField()
    referer = models.TextField(blank=True)
    unique_visit = models.BooleanField()

    @staticmethod
    def create_from_request(request):
        project = Project.objects.get(tid=request.GET.get('tid'))
        parsed_url = urlparse(request.GET.get('url'))
        ref = request.GET.get('ref')

        # A unique visit is when referrer domain is not the current domain.
        # which means the user is coming from outside the site's domain
        unique_visit = urlparse(ref).netloc != parsed_url.netloc

        # Set referrer to source (email, etc.) if found in site url query
        source = re.search(r'(?<=ref=)\S*', parsed_url.query)
        if source:
            source = source.group(0)
        referer = ref or source

        return PageView.objects.create(
            project=project,
            protocol=parsed_url.scheme,
            domain=parsed_url.netloc,
            path=parsed_url.path,
            url=request.GET.get('url'),
            title=request.GET.get('t') or '',
            window_width=request.GET.get('wiw') or '0',
            window_height=request.GET.get('wih') or '0',
            referer=referer or '',
            unique_visit=unique_visit
        )
