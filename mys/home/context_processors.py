from .models import CompanyPage, NewsPage, HomePage, AccessPage, BlogIndexPage


def global_context(request):
    context = {}

    home_page = HomePage.objects.live().first()
    if home_page:
        context['home_page'] = home_page

    company_page = CompanyPage.objects.live().first()
    if company_page:
        context['company_page'] = company_page

    news_page = NewsPage.objects.live().first()
    if news_page:
        context['news_page'] = news_page

    access_page = AccessPage.objects.live().first()
    if access_page:
        context['access_page'] = access_page

    blog_page = BlogIndexPage.objects.live().first()
    if blog_page:
        context['blog_page'] = blog_page

    return context
