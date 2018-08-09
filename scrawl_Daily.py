#coding=utf-8
import core
import model
import settings
import woaiwojialib

def get_communitylist():
	res = []
	for community in model.Community.select():
		res.append(community.title)
	return res
def get_soldHouseList():
    res = []
    for house in model.Monthsellinfo.select().where(model.Monthsellinfo.dealdate.contains(u'30天')):
        res.append(house.houseID)
    return res

def get_sellingHouseList():
    res = []
    for house in model.Houseinfo.select():
        res.append(house.houseID)
    return res

if __name__=="__main__":
    pages = settings.PAGES
    regionlist = settings.REGIONLIST # only pinyin support
    #model.database_init()
    #core.GetHouseByRegionlist(regionlist,pages)
    #core.GetRentByRegionlist(regionlist,pages)
    #core.GetCommunityByRegionlist(regionlist) # Init,scrapy celllist and insert database; could run only 1st time
    #communitylist = get_communitylist() # Read celllist from database
    #core.GetHouseByCommunitylist(communitylist,pages)
    #core.GetRentByCommunitylist(communitylist,pages)
    #core.GetSellByCommunitylist(communitylist,pages)
    #woaiwojialib.GetSellByCommunitylist()
    soldhouselist = get_soldHouseList()
    core.GetSellByHouselist(soldhouselist)
    #sellinghouselist = get_sellingHouseList()
    #core.GetSellByHouselist(sellinghouselist)