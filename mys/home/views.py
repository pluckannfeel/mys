from django.http import Http404
from django.shortcuts import render
from django.views.generic import View
from .models import HomePage, NewsPage
# views.py
from django.views.generic import TemplateView


class NewsDetailView(View):
    def get(self, request, news_item_slug):
        try:
            home_page = HomePage.objects.live().first()
            news_page = NewsPage.objects.live().first()
            if not news_page:
                raise Http404("No news page found")
            news_item = next(
                (item.value for item in news_page.news_items if item.value['slug'] == news_item_slug), None)
            if not news_item:
                raise Http404("News item not found")
            return render(request, 'home/news_detail_page.html', {
                'home_page': home_page,
                'news_page': news_page,
                'news_item': news_item,
                'footer': home_page.footer,  # Pass footer content
            })
        except NewsPage.DoesNotExist:
            raise Http404("News item not found")
