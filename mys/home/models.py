from django.db import models
from django import forms
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import StreamField, RichTextField
from wagtail.blocks import StructBlock, CharBlock, TextBlock, RichTextBlock, PageChooserBlock, DateBlock, URLBlock, ListBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet
from django.utils.text import slugify
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class SocialLinkBlock(StructBlock):
    # FontAwesome icon class, e.g., 'fab fa-facebook-f'
    icon = CharBlock(required=True, max_length=50)
    url = URLBlock(required=True)


class FooterBlock(StructBlock):
    logo = ImageChooserBlock(required=True)
    address = RichTextBlock(required=True)
    socials = ListBlock(SocialLinkBlock())
    copyright = RichTextBlock(required=True)

    class Meta:
        template = "blocks/footer_block.html"
        icon = "placeholder"
        label = "Footer"


class AccessPage(Page):
    jumbotron_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    page_title_en = models.CharField(
        max_length=255, blank=True, verbose_name=_("Page Title (English)"))
    page_title_ja = models.CharField(
        max_length=255, blank=True, verbose_name=_("Page Title (Japanese)"))
    subtitle_en = RichTextField(
        blank=True, verbose_name=_("Subtitle (English)"))
    subtitle_ja = RichTextField(
        blank=True, verbose_name=_("Subtitle (Japanese)"))
    gallery = StreamField(
        [
            ('image', ImageChooserBlock())
        ],
        blank=True,
        use_json_field=True
    )

    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('jumbotron_image'),
        FieldPanel('page_title_en'),
        FieldPanel('page_title_ja'),
        FieldPanel('subtitle_en'),
        FieldPanel('subtitle_ja'),
        FieldPanel('gallery'),
        FieldPanel('footer'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = []

    def get_context(self, request):
        context = super().get_context(request)
        context['breadcrumbs'] = [
            {'title': 'Home', 'url': self.get_parent().url},
            {'title': self.page_title_en if request.LANGUAGE_CODE ==
                'en' else self.page_title_ja, 'url': self.url},
        ]
        return context


class CarouselSlideBlock(StructBlock):
    image = ImageChooserBlock()
    caption = CharBlock(required=False, max_length=250)

    class Meta:
        template = "blocks/carousel_slide_block.html"


class SubMenuSectionBlock(StructBlock):
    image = ImageChooserBlock()
    title = CharBlock(required=True, max_length=100)
    body = TextBlock(required=True)

    class Meta:
        template = "blocks/sub_menu_section_block.html"


class SloganBlock(StructBlock):
    top_image = ImageChooserBlock(required=True)
    title = CharBlock(required=True)
    body = RichTextBlock(required=True)
    bottom_image = ImageChooserBlock(required=True)

    class Meta:
        template = "blocks/slogan_block.html"


class CampaignBlock(StructBlock):
    image = ImageChooserBlock(required=True)
    title = CharBlock(required=True, max_length=100)
    details = TextBlock(required=True)

    class Meta:
        template = "blocks/campaign_block.html"


class BlogBlock(StructBlock):
    class Meta:
        template = "blocks/blog_block.html"
        icon = "edit"
        label = "Blog Block"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        blog_index_page = BlogIndexPage.objects.live().first()
        if blog_index_page:
            context['posts'] = BlogPage.objects.live(
            ).descendant_of(blog_index_page)[:6]
        else:
            context['posts'] = []
        return context


@register_snippet
class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    page = ParentalKey(
        'BlogPage', related_name='blog_categories', on_delete=models.CASCADE)
    category = models.ForeignKey(
        'Category', related_name='+', on_delete=models.CASCADE)

    panels = [
        FieldPanel('category'),
    ]


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    categories = ParentalManyToManyField(
        'Category', through=BlogCategory, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('header_image'),
        InlinePanel('blog_categories', label="Categories"),
    ]

    parent_page_types = ['home.BlogIndexPage']
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['footer'] = self.get_parent().specific.footer
        context['parent_page'] = self.get_parent()
        context['jumbotron_image'] = self.get_parent().specific.jumbotron_image
        context['categories'] = Category.objects.all()
        context['recent_posts'] = BlogPage.objects.live().order_by('-date')[:5]
        return context


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    jumbotron_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('jumbotron_image'),
        FieldPanel('footer'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        category_id = request.GET.get('category')
        if category_id:
            all_posts = BlogPage.objects.live().descendant_of(self).filter(
                blog_categories__category__id=category_id).order_by('-first_published_at')
        else:
            all_posts = BlogPage.objects.live().descendant_of(
                self).order_by('-first_published_at')

        paginator = Paginator(all_posts, 6)  # Show 6 posts per page
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['posts'] = posts
        context['categories'] = Category.objects.all()
        return context

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.BlogPage']


class NewsItemBlock(StructBlock):
    date = DateBlock(required=True)
    title = CharBlock(required=True, max_length=250)
    slug = CharBlock(required=True, max_length=250)
    body = RichTextBlock(required=True)
    image = ImageChooserBlock(required=False)

    class Meta:
        template = "blocks/news_item_block.html"


class NewsDetailPage(Page):
    parent_page_types = ['home.NewsPage']
    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('footer'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        news_item_slug = kwargs.get('slug')
        news_items = self.get_parent().specific.news_items

        news_item = next(
            (item.value for item in news_items if item.value['slug'] == news_item_slug), None)
        if not news_item:
            raise Http404("News item not found")

        # add footer to context (from news page)
        context['footer'] = self.get_parent().specific.footer

        context['news_item'] = news_item

        return context


class NewsPage(Page):
    intro = RichTextField(blank=True)
    jumbotron_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    slogan_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    news_items = StreamField(
        [("news_item", NewsItemBlock())], blank=True, use_json_field=True)

    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('jumbotron_image'),
        FieldPanel('slogan_photo'),
        FieldPanel('news_items'),
        FieldPanel('footer'),
    ]

    subpage_types = ['NewsDetailPage']

    def get_context(self, request):
        context = super().get_context(request)
        context['news_items'] = self.news_items

        # Get the home page
        home_page = HomePage.objects.live().first()
        context['home_page'] = home_page

        return context


# models.py
class TeamMember(Orderable):
    id = models.AutoField(primary_key=True)
    page = ParentalKey(
        'CompanyPage', related_name='team_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    photo = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name='+'
    )
    hover_photo = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name='+', blank=True, null=True
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('photo'),
        FieldPanel('hover_photo'),
    ]


class CompanyPhoto(Orderable):
    id = models.BigAutoField(primary_key=True)
    page = ParentalKey('CompanyPage', related_name='company_photos')
    photo = models.ForeignKey('wagtailimages.Image',
                              on_delete=models.CASCADE, related_name='+')

    panels = [FieldPanel('photo')]


class CompanyPage(Page):
    jumbotron_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    company_title_en = models.CharField(
        max_length=255, blank=True, verbose_name=_("Company Title (English)"))
    company_title_ja = models.CharField(
        max_length=255, blank=True, verbose_name=_("Company Title (Japanese)"))
    company_introduction_en = RichTextField(
        blank=True, verbose_name=_("Company Introduction (English)"))
    company_introduction_ja = RichTextField(
        blank=True, verbose_name=_("Company Introduction (Japanese)"))
    team_title_en = models.CharField(
        max_length=255, blank=True, verbose_name=_("Team Title (English)"))
    team_title_ja = models.CharField(
        max_length=255, blank=True, verbose_name=_("Team Title (Japanese)"))
    introduction_en = RichTextField(
        blank=True, verbose_name=_("Introduction (English)"))
    introduction_ja = RichTextField(
        blank=True, verbose_name=_("Introduction (Japanese)"))

    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('jumbotron_image'),
        FieldPanel('company_title_en'),
        FieldPanel('company_title_ja'),
        FieldPanel('company_introduction_en'),
        FieldPanel('company_introduction_ja'),
        InlinePanel('company_photos', label="Company Photos"),
        FieldPanel('team_title_en'),
        FieldPanel('team_title_ja'),
        FieldPanel('introduction_en'),
        FieldPanel('introduction_ja'),
        InlinePanel('team_members', label="Team Members"),
        FieldPanel('footer'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = []

    def get_context(self, request):
        context = super().get_context(request)
        home_page = HomePage.objects.live().first()
        context['home_page'] = home_page
        return context


class HomePage(Page):
    header = RichTextField(blank=True)
    carousel = StreamField([("slide", CarouselSlideBlock())],
                           blank=True, use_json_field=True)
    sub_menu_sections = StreamField(
        [("section", SubMenuSectionBlock())], blank=True, use_json_field=True)
    slogan = StreamField([("slogan", SloganBlock())],
                         blank=True, use_json_field=True)
    campaigns = StreamField([("campaign", CampaignBlock())],
                            blank=True, use_json_field=True)
    blog_items = StreamField(
        [("blog_item", BlogBlock())], blank=True, use_json_field=True)
    footer = StreamField([('footer', FooterBlock())],
                         blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('header'),
            ],
            heading="Page Sections",
        ),
        FieldPanel('carousel'),
        FieldPanel('sub_menu_sections'),
        FieldPanel('slogan'),
        FieldPanel('campaigns'),
        FieldPanel('blog_items'),  # Added FieldPanel for blog_items
        FieldPanel('footer'),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        company_page = CompanyPage.objects.live().first()

        if not company_page:
            raise ValueError(
                "No live CompanyPage found. Please create and publish a CompanyPage in the admin interface.")

        context['company_page'] = company_page

        news_page = NewsPage.objects.live().first()
        if not news_page:
            raise ValueError(
                "No live NewsPage found. Please create and publish a NewsPage in the admin interface.")
        context['news_page'] = news_page

        # Adding blog items to the context
        blog_index_page = BlogIndexPage.objects.live().first()
        if blog_index_page:
            context['blog_items'] = BlogPage.objects.live().descendant_of(blog_index_page)[:6]
        else:
            context['blog_items'] = []

        return context

    def save(self, *args, **kwargs):
        for news_item in self.news_items:
            if news_item.block_type == 'news_item' and not news_item.value['slug']:
                news_item.value['slug'] = slugify(news_item.value['title'])
        super().save(*args, **kwargs)