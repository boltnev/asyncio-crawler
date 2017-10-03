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


def info(url, resp, num_worker):
    print("{} STATUS:{} {}".format(num_worker, resp.status, url))


class Crawler:

    def __init__(self, rooturl, loop, max_workers=10):
        self.rooturl = rooturl
        self.loop = loop
        self.queue = [self.rooturl]
        self.in_process = []
        self.seen = []
        self.max_workers = max_workers

    async def work(self, session, num_worker):
        while self.queue or self.in_process:
            if len(self.queue) == 0:
                await asyncio.sleep(1)
                continue
            url = self.queue.pop(0)
            self.in_process.append(url)
            await self.handle_url(url, session, num_worker)
            self.in_process.remove(url)

    async def handle_url(self, url, session, num_worker):
        #print("{} start handling {}".format(num_worker, url))
        async with session.get(url) as resp:
            info(url, resp, num_worker)
            self.seen.append(url)
            if resp.status // 100 == 2:
                html = await resp.text()
                links = extract_links(self.rooturl, html)
                for link in links:
                    if link not in self.queue \
                        and link not in self.seen \
                        and link not in self.in_process:
                        self.queue.append(link)

        #print("{} stop handling {}".format(num_worker, url))

    async def start(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for i in range(self.max_workers):
                task = self.loop.create_task(self.work(session, i))
                tasks.append(task)
            await asyncio.wait(tasks)


if __name__=="__main__":
    rooturl = sys.argv[1]
    loop = asyncio.get_event_loop()
    crawler = Crawler(rooturl, loop)
    loop.run_until_complete(crawler.start())
