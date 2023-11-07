from .common import InfoExtractor
from .vimeo import VHXEmbedIE

from lxml import html

_IGNORE_DESCRIPTION_LINES = (
    "Watch this video and more on History Hit",
    "Already subscribed?",
    "the functionality of our website,",
)
EMBED_URL_PATTERN = r'embed_url: "(?P<url>https://embed.vhx.tv/videos/[-a-zA-Z0-9@;:%._\\+~#?&//=]*)"'


class HistoryHitIE(InfoExtractor):
    IE_NAME = 'historyhit.com'
    _VALID_URL = r'https://access.historyhit\.com?[a-z0-9\-/]+/videos/(?P<id>[a-zA-Z0-9-]+)'
    _TESTS = [{
        'url': 'https://access.historyhit.com/videos/the-incredible-story-of-william-j-bankes-adventurer-collector-spy',
        'info_dict': {
            'id': 'the-incredible-story-of-william-j-bankes-adventurer-collector-spy',
            'ext': 'mp4',
            'title': 'The Incredible Story of William J. Bankes - Adventurer, Collector, Spy',
        },
    }]

    def _real_extract(self, url):
        internal_id = self._match_id(url)
        contents = self._download_webpage(url, internal_id)
        tree = html.fromstring(contents)

        title = tree.xpath('//h1/strong/text()')[0]
        description = tree.xpath('//div[contains(@class, "text")]/p/text()')
        description = " ".join(
            text for text in description
            if not any(line in text for line in _IGNORE_DESCRIPTION_LINES)
        ).strip()

        # extract uncompressed thumbnail
        thumbnail = self._og_search_thumbnail(contents)
        thumbnail = thumbnail.split('?')[0] if thumbnail else None

        # TODO find release date

        # TODO find series (if any!)

        # extract the embed URL
        embed_url = self._search_regex(EMBED_URL_PATTERN, contents, "embed_url")
        vhx_url = VHXEmbedIE._smuggle_referrer(embed_url, 'https://access.historyhit.com')
        vhx_id = self._search_regex(r'embed\.vhx\.tv/videos/(.+?)\?', embed_url, 'vhx_id')

        return {
            '_type': 'url_transparent',
            'ie_key': VHXEmbedIE.ie_key(),
            'id': vhx_id,
            'url': vhx_url,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }
