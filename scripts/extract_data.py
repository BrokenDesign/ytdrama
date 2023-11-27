import logging
from ytdrama.settings import config
from ytdrama.youtube import scrape

logger = logging.getLogger(__name__)

for channel in config.channels:
    logger.info(f"Scraping channel: {channel.name} ({channel.id})")
    scrape([channel.id])

print("Finished")