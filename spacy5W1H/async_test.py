# -*- coding: utf-8 -*-
import requests
import time
import asyncio
import functools

# =============================================================================
# 
# def w3req():
#     for i in range(10):
#         x = requests.get('https://w3schools.com/python/demopage.htm')
#         #print(x.text)
#     
# t1=time.time()    
# w3req()
# print("normal time_taken:: ",time.time()-t1)    
# =============================================================================


# =============================================================================
# async def w3req():
#     for i in range(10):
#         loop = asyncio.get_event_loop()
#         func = functools.partial(requests.get,url='https://w3schools.com/python/demopage.htm')
#         req=loop.run_in_executor(None,func)
#         x = await req
#         print(x.text)
#     
# t1=time.time()    
# loop = asyncio.get_event_loop()
# loop.run_until_complete(w3req())    
# print("async time_taken:: ",time.time()-t1)    
# 
# =============================================================================

async def w3req():
    async for i in range(10):
        loop = asyncio.get_event_loop()
        print("request no:: ",i)
        func = functools.partial(requests.get,url='https://w3schools.com/python/demopage.htm')
        req=loop.run_in_executor(None,func)
        x = await req
        print(x.text)
    
t1=time.time()    
loop = asyncio.get_event_loop()
loop.run_until_complete(w3req())
print("async time_taken:: ",time.time()-t1)    


import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm',
            'https://w3schools.com/python/demopage.htm'
        ]
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))
        htmls = await asyncio.gather(*tasks)
        for html in htmls:
            print(html[:100])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())