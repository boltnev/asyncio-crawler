#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import asyncio

import aiohttp
from lxml import html


def extract_links(rooturl, text):
    try:
        dom = html.fromstring(text)
    except ValueError:
        return []
    links = []
    for a in dom.findall(".//a"):
        href = a.attrib.get('href', '')
        if href.startswith("/"):
            link = rooturl+href.strip()
            if link not in links:
                links.append(link)
    return links


def info(url, resp):
    print("{} STATUS:{}".format(url, resp.status))


async def start(rooturl):
    queue = [rooturl]
    seen = []
    while queue:
        url = queue.pop(0)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                info(url, resp)
                seen.append(url)
                if resp.status // 100 == 2:
                    html = await resp.text()
                    links = extract_links(rooturl, html)
                    for link in links:
                        if link not in queue and link not in seen:
                            queue.append(link)


if __name__=="__main__":
    rooturl = sys.argv[1]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(rooturl))
