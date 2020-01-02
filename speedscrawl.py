# coding=utf-8
import model
import settings
from multiprocessing import Pool
import time
import asyncio
import aiohttp 
import speedcore


def get_communitylist():
    res = []
    for community in model.Community.select():
        res.append((community.title, community.id))
    return res



async def get_community_and_house(regionlist):
    semaphore = asyncio.Semaphore(500) # 限制并发量为500
    # await speedcore.GetCommunityByRegionlist(regionlist, semaphore)  # Init,scrapy celllist and insert database; could run only 1st time
    communitylist = get_communitylist()  # Read celllist from database
    await speedcore.GetHouseByCommunitylist(communitylist, semaphore)


if __name__ == "__main__":
    pages = settings.PAGES
    regionlist = settings.REGIONLIST  # only pinyin support
    model.database_init()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_community_and_house(regionlist))


