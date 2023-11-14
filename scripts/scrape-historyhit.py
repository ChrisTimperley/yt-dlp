#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import typing as t

import requests
from lxml import html

VALID_URL = re.compile(r'https://access.historyhit\.com?[a-z0-9\-/]+/videos/(?P<id>[0-9a-zA-Z-]+)')


def fetch_urls_from_html_contents(contents: str, urls: t.Set[str]) -> None:
    tree = html.fromstring(contents)
    for link_tag in tree.xpath('//a'):
        link_url = link_tag.attrib.get("href")
        if link_url is not None and VALID_URL.match(link_url):
            video_filename = link_url.split('/')[-1]
            canonical_url = f"https://access.historyhit.com/videos/{video_filename}"
            urls.add(canonical_url)


def fetch_urls_from_page(url: str, page: int, urls: t.Set[str]) -> None:
    page_url = f"{url}?html=1&page={page}&ajax=1"
    r = requests.get(page_url)
    fetch_urls_from_html_contents(r.text, urls)


def fetch_urls(url: str) -> t.Set[str]:
    urls: t.Set[str] = set()
    r = requests.get(url)
    contents = r.text

    fetch_urls_from_html_contents(contents, urls)
    for i in range(2, 6):
        fetch_urls_from_page(url, i, urls)
    return urls


def main() -> None:
    urls = fetch_urls("https://access.historyhit.com/20th-century")
    for url in sorted(urls):
        print(url)


if __name__ == "__main__":
    main()
