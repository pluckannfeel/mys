from django.core.management.base import BaseCommand
from home.models import HomePage  # Adjust 'home' to your actual app name
from wagtail.blocks.stream_block import StreamValue

class Command(BaseCommand):
    help = 'Clear link values in NewsItemBlock'

    def handle(self, *args, **kwargs):
        home_pages = HomePage.objects.all()

        for home_page in home_pages:
            news_items = home_page.news_items

            new_news_items = []
            for block in news_items:
                if block.block_type == 'news_item':
                    block.value['link'] = None  # Clear the link value
                new_news_items.append(block)

            # Update the news_items StreamField
            home_page.news_items = StreamValue(news_items.stream_block, new_news_items, is_lazy=True)

            # Save the changes to the HomePage
            home_page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS('Successfully cleared link values in NewsItemBlock'))
