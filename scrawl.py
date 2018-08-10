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

def get_custom_communitylist():
	res = []
	res.append(u'木樨地')
	res.append(u'物资大院')
	res.append(u'三里河北街3号院')
	res.append(u'三里河北街5号院')
	res.append(u'真武庙')
	return res
	
if __name__=="__main__":
    pages = settings.PAGES
    regionlist = settings.REGIONLIST # only pinyin support
    model.database_init()
    core.GetHouseByRegionlist(regionlist,pages)
    core.GetRentByRegionlist(regionlist,pages)
    core.GetCommunityByRegionlist(regionlist) # Init,scrapy celllist and insert database; could run only 1st time
    custom_l = get_custom_communitylist()
    core.GetCommunityByCustomlist(custom_l)
    communitylist = get_communitylist() # Read celllist from database
    core.GetHouseByCommunitylist(communitylist,pages)
    core.GetRentByCommunitylist(communitylist,pages)
    core.GetSellByCommunitylist(communitylist,pages)
    #woaiwojialib.GetSellByCommunitylist()
