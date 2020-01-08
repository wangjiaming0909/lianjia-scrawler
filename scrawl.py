# coding=utf-8
import core
import model
import settings
from multiprocessing import Pool
import time
#import woaiwojialib


def get_communitylist():
    res = []
    for community in model.Community.select(model.Community.title, model.Community.id).order_by(model.Community.id):
        res.append((community.title, community.id))
    return res


def get_custom_communitylist():
    res = [u'新龙城', u'物资大院', u'三里河北街3号院', u'三里河北街5号院', u'真武庙']
    # res = [u'新龙城']
    return res


if __name__ == "__main__":
    pages = settings.PAGES
    regionlist = settings.REGIONLIST  # only pinyin support
    # model.database_init()

    # core.GetHouseByRegionlist(regionlist, pages)
    # core.GetRentByRegionlist(regionlist, pages)
    
    # custom_l = get_custom_communitylist()
    #core.GetCommunityByCustomlist(custom_l)
    
    pool = Pool(processes=4)
    pool.map(core.get_community_perregion, regionlist)
    
    core.GetCommunityByRegionlist(regionlist)  # Init,scrapy celllist and insert database; could run only 1st time

    communitylist = get_communitylist()  # Read celllist from database
    # for communityInfo in communitylist:
    #     pool.apply_async(core.get_house_percommunity, args= communityInfo)
    #
    # pool.close()  # 关闭进程池，不再接受新的进程
    # pool.join()  # 主进程阻塞等待子进程的退出
    
    core.GetHouseByCommunitylist(communitylist, pages)
    
    #core.GetSellByCommunitylist(communitylist, pages)

    # core.GetRentByCommunitylist(communitylist, pages)
    # woaiwojialib.GetSellByCommunitylist()
