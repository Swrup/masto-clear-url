"""
Mastodon bot to clean URLs
"""
from mastodon import Mastodon, StreamListener
from urllib.parse import urlparse
import validators
from bs4 import BeautifulSoup
import ClearURLsCore
import signal

mastodon = Mastodon(
    #file with your account token
    access_token='token.secret',
    #instance url
    api_base_url=''
)

class Listener(StreamListener):
    def on_update(self, toot):
        """A new status has appeared! 'status' is the parsed JSON dictionary
        describing the status."""
        content = toot.content
        soup = BeautifulSoup(content, 'html.parser')
        cleaned_urls = []
        unclean = False
        for link in soup.find_all('a'):
            url = link.get('href')
            if validators.url(url):
                clean_url = cleaner.clean(url)
                if clean_url != url:
                    #if clean_url and url are almost the same size its porbably
                    #too spammy to toot about it
                    if abs(len(clean_url) - len(url)) < 6:
                        continue
                    cleaned_urls.append(clean_url)
                    unclean = True
    
        #reply
        if unclean:
            idempotency_key = str(toot.id)
            to_status = toot
            plural = ""
            if len(cleaned_urls) > 1:
                plural = "s"
    
            status = "The URL" + plural + " you posted contains trackers!\nI cleaned it for you:\n\r"
            for clean_url in cleaned_urls:
                status = status + clean_url + "\n"
    
            mastodon.status_reply(to_status, status, in_reply_to_id=toot.id, media_ids=None, sensitive=False, visibility="public", spoiler_text=None, language="en", idempotency_key=idempotency_key, content_type=None, scheduled_at=None, poll=None, untag=True)

is_healthy = mastodon.stream_healthy()

listener = Listener()
cleaner = ClearURLsCore.ClearURLsCore()

handle = mastodon.stream_local(listener, run_async=True, timeout=300, \
            reconnect_async=False, reconnect_async_wait_sec=5)

signal.pause()
