#!/usr/bin/python
import asyncio
import aiohttp
import aiofiles as aiof
import os
import json


EXPORT_DIR = "."
STATIC_DIR = "../tommoral.django.local/CV/static/CV"


async def fetch_page(session, url, fname=None):
    print(url)
    async with session.get(url) as response:
        assert response.status == 200
        content = await response.read()
        content = content.replace(b"/static/CV", b"")
        if fname is not None:
            async with aiof.open(os.path.join(EXPORT_DIR, fname), mode='wb') as f:
                await f.write(content)
        return content


async def sync_static_files(fname):
    fname_in = os.path.join(STATIC_DIR, fname)
    fname_out = os.path.join(EXPORT_DIR, fname)
    async with aiof.open(fname_in, "rb") as f_in:
        async with aiof.open(fname_out, "wb") as f_out:
            async for line in f_in:
                await f_out.write(line)
            await f_out.flush()


async def sync_images():
    image_dir = os.path.join(STATIC_DIR, "images")
    images = os.listdir(image_dir)
    fs = []
    for im in images:
        f_im = os.path.join("images", im)
        fs += [sync_static_files(f_im)]
    await asyncio.gather(*fs)


async def main():
    async with aiohttp.ClientSession() as session:
        grants = await fetch_page(
            session, "http://127.0.0.1:8000/list_grants/"
        )
        print(grants)
        await fetch_page(session, 'http://127.0.0.1:8000/about/',
                         "about.html"),
        await fetch_page(session, 'http://127.0.0.1:8000/publications/',
                         "publications.html"),
        await fetch_page(session, 'http://127.0.0.1:8000/talks/',
                         "talks.html"),
        await fetch_page(session, 'http://127.0.0.1:8000/oss/',
                         "oss.html"),
        await fetch_page(session, 'http://127.0.0.1:8000/grants/',
                         "grants.html"),
        await fetch_page(session, 'http://127.0.0.1:8000/peoples/',
                         "people.html"),
        await sync_static_files("css/style.css"),
        await sync_static_files("javascript/lib.js"),
        await sync_images()
        grants = json.loads(grants)['grants']
        for g in grants:
            await fetch_page(
                session, f"http://127.0.0.1:8000/{g}/", f"{g}.html"
            )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
