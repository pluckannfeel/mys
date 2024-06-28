from django.core.management.base import BaseCommand
from home.models import BlogPage, BlogIndexPage, BlogCategory, Category

class Command(BaseCommand):
    help = 'Clears all data in the blog-related tables'

    def handle(self, *args, **kwargs):
        BlogCategory.objects.all().delete()
        BlogPage.objects.all().delete()
        BlogIndexPage.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared blog data'))
