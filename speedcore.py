# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import settings
import model
import speedmisc
import time
import datetime
import urllib.request as urllib2
import logging
import asyncio
import aiohttp 

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
BASE_URL = u"http://%s.lianjia.com/" % (settings.CITY)
CITY = settings.CITY


# =============================Public========================================================

async def GetHouseByCommunitylist(communitylist, semaphore, _page=None):
    logging.info("Get House Infomation")
    starttime = datetime.datetime.now()
    community_len = str(len(communitylist))
    tasks = []
    for community, id in communitylist:
        logging.info("communitylist: " + community + " " + "/" + community_len)
        task = asyncio.ensure_future(get_house_percommunity(community, id, semaphore, _page))
        tasks.append(task)
    await asyncio.wait(tasks)
    endtime = datetime.datetime.now()
    logging.info("Get House Run time: " + str(endtime - starttime))

async def GetCommunityByRegionlist(regionlist, semaphore):
    logging.info("Get Community Infomation")
    starttime = datetime.datetime.now()
    regionlist_len = str(len(regionlist))
    tasks = []
    
    for regionname in regionlist:
        logging.info("regionlist: " + "/" + regionname)
        task = asyncio.ensure_future(get_community_perregion(regionname, semaphore))
        tasks.append(task)
    
    await asyncio.wait(tasks)

    endtime = datetime.datetime.now()
    logging.info("Get Community Run time: " + str(endtime - starttime))


# =====================Private=============================================================================

async def get_house_percommunity(communityname, id, semaphore, _page=None):
    url = BASE_URL + u"ershoufang/rs" + urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = await speedmisc.get_source_code(url, semaphore)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    total_pages = _page
    if total_pages == None:
        total_pages = speedmisc.get_total_pages(source_code)

    if total_pages == None:
        row = model.Houseinfo.select().count()
        return
        # raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page == 0:
            url_page = BASE_URL + u"ershoufang/rs" + urllib2.quote(communityname.encode('utf8')) + "/"
        if page > 0:
            url_page = BASE_URL + u"ershoufang/pg%drs%s/" % (page, urllib2.quote(communityname.encode('utf8')))
        
        await get_perpage_house(url_page, communityname, id, page, total_pages, semaphore)
            
            
async def get_perpage_house(url, communityname, id, page, total_pages, semaphore):
        log_progress("GetHouseByCommunitylist", communityname, page + 1, total_pages)
        
        source_code = await speedmisc.get_source_code(url, semaphore)
        if source_code == None:
            return 
        soup = BeautifulSoup(source_code, 'lxml')
        nameList = soup.findAll("li", {"class": "clear"})
        data_source = []
        hisprice_data_source = []
        i = 0
        for name in nameList:  # per house loop
            i = i + 1
            info_dict = {}
            try:
                position = name.find("div", {"class": "positionInfo"})
                exact_community = position.a.get_text().strip()
                if exact_community != communityname:
                    logging.info('expected community: ' + communityname + ' actual: ' + exact_community)
                    continue
                #if("小区" not in communityname and "社区" not in communityname):
                #    if(exact_community != communityname):
                #        logging.info(communityname + "search failed! please check")
                #        continue

                totalPrice = name.find("div", {"class": "totalPrice"})
                totalPrice = totalPrice.span.get_text()
                info_dict.update({u'totalPrice': totalPrice})

                unitPrice = name.find("div", {"class": "unitPrice"})
                hid = unitPrice.get('data-hid')
                info_dict.update({u'houseID': hid})
                info_dict.update({u'unitPrice': unitPrice.get('data-price')})

                # find the latest totalprice, if the price is the same as the price we get this time, skip updating the hisprice
                needUpdateHisPrice = True
                maxDate = model.Hisprice.select(model.fn.MAX(model.Hisprice.date)).where(model.Hisprice.houseID == hid).scalar()
                ret = model.Hisprice.get_or_none((model.Hisprice.houseID == hid) & (model.Hisprice.date == maxDate) & (model.Hisprice.totalPrice == totalPrice))

                if ret is not None:
                    print(ret.houseID, ' ', ret.date, ' ', ret.totalPrice, ' price not change, skipping...')
                    needUpdateHisPrice = False
                else:
                    print(hid, ' new entry added...')

                housetitle = name.find("div", {"class": "title"})
                info_dict.update({u'title': housetitle.a.get_text().strip()})
                info_dict.update({u'link': housetitle.a.get('href')})
                
                imgUrl = name.find("img", {"class": "lj-lazy"})
                info_dict.update({u'imgUrl': imgUrl.get('src')})

                houseaddr = name.find("div", {"class": "address"})
                if CITY == 'bj':
                    info = houseaddr.div.get_text().split('|')
                else:
                    info = houseaddr.div.get_text().split('|')

                info_dict.update({u'communityName': communityname})
                info_dict.update({u'communityID': id})
                info_dict.update({u'housetype': info[0].strip()})
                info_dict.update({u'square': info[1].strip()})
                info_dict.update({u'direction': info[2].strip()})
                info_dict.update({u'decoration': info[3].strip()})
                info_dict.update({u'floor': info[4].strip()})
                info_dict.update({u'years': info[5].strip()})
                
                followInfo = name.find("div", {"class": "followInfo"})
                info_dict.update({u'followInfo': followInfo.get_text()})

                tax = name.find("div", {"class": "tag"})
                info_dict.update({u'taxtype': tax.get_text().strip()})

                totalPrice = name.find("div", {"class": "totalPrice"})
                info_dict.update({u'totalPrice': totalPrice.span.get_text()})

                unitPrice = name.find("div", {"class": "unitPrice"})
                info_dict.update({u'unitPrice': unitPrice.get('data-price')})
                info_dict.update({u'houseID': unitPrice.get('data-hid')})
            except:
                continue
            # houseinfo insert into mysql
            data_source.append(info_dict)
            hisprice_data_source.append({"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})
            
            # model.Houseinfo.insert(**info_dict).execute()
            # model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).execute()
        
        try:
            with model.database.atomic():
                model.Houseinfo.insert_many(data_source).execute()
                model.Hisprice.insert_many(hisprice_data_source).execute()
            time.sleep(1)
        except Exception as e:
            logging.error(e)
            logging.info(communityname + "percommunity page: " + str(page) + " Fail")

async def get_community_perregion(regionname, semaphore):
    url = BASE_URL + u"xiaoqu/" + regionname + "/"
    print(url)
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,timeout=10) as resp:
                source_code = await resp.text()
                soup = BeautifulSoup(source_code, 'lxml')
                if check_block(soup):
                    return
                total_pages = speedmisc.get_total_pages(source_code)
                if total_pages == None:
                    row = model.Community.select().count()
                    raise RuntimeError("Finish at %s because total_pages is None" % row)
    
    tasks = []

    for page in range(total_pages):
        if page == 0: 
            url_page = BASE_URL + u"xiaoqu/" + regionname + "/"
        if page > 0:
            url_page = BASE_URL + u"xiaoqu/" + regionname + "/pg%d/" % page
        
        # task = asyncio.ensure_future(get_per_community_info(url_page, page, regionname, total_pages))
        # tasks.append(task)
        await get_perpage_community_info(url_page, page, regionname, total_pages, semaphore)
    
    
async def get_perpage_community_info(url, page, regionname, total_pages, semaphore):
    source_code = await speedmisc.get_source_code(url, semaphore)
    soup = BeautifulSoup(source_code, 'lxml')
    nameList = soup.findAll("li", {"class": "clear"})
    log_progress("GetCommunityByRegionlist", regionname, page + 1, total_pages)
    data_source = []
    i = 0
    for name in nameList:  # Per house loop
        i = i + 1
        info_dict = {}
        try:
            communitytitle = name.find("div", {"class": "title"})
            title = communitytitle.get_text().strip('\n')
            link = communitytitle.a.get('href')
            info_dict.update({u'title': title})
            print(title)
            info_dict.update({u'link': link})

            district = name.find("a", {"class": "district"})
            info_dict.update({u'district': district.get_text()})

            bizcircle = name.find("a", {"class": "bizcircle"})
            info_dict.update({u'bizcircle': bizcircle.get_text()})

            tagList = name.find("div", {"class": "tagList"})
            info_dict.update({u'tagList': tagList.get_text().strip('\n')})

            onsale = name.find("a", {"class": "totalSellCount"})
            info_dict.update({u'onsale': onsale.span.get_text().strip('\n')})

            onrent = name.find("a", {"title": title + u"租房"})
            info_dict.update({u'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

            info_dict.update({u'id': str(name.get('data-housecode'))})

            price = name.find("div", {"class": "totalPrice"})
            info_dict.update({u'price': price.span.get_text().strip('\n')})

            communityinfo = await get_detail_communityinfo_by_url(link, semaphore)
            for key, value in communityinfo.items():
                info_dict.update({key: value})


        except Exception as e:
            logging.error(e)
            logging.info("page:" + page + "name:" + name + "Fail")
            continue

        try:
            with model.database.atomic():
                model.Community.replace_many(info_dict).execute()
            time.sleep(1)
        except Exception as e:
            logging.error(e)
            logging.info(regionname + "page:" + page + "Fail")
            continue

        # communityinfo insert into mysql
        # data_source.append(info_dict)
        # model.Community.insert(**info_dict).execute()

async def get_detail_communityinfo_by_url(url, semaphore):
    source_code = await speedmisc.get_source_code(url, semaphore)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class": "xiaoquInfoItem"})
    res = {}
    for info in communityinfos:
        key_type = {
            u"建筑年代": u"year",
            u"建筑类型": u"housetype",
            u"物业费用": u"cost",
            u"物业公司": u"service",
            u"开发商": u"company",
            u"楼栋总数": u"building_num",
            u"房屋总数": u"house_num",
        }
        try:
            key = info.find("span", {"xiaoquInfoLabel"})
            value = info.find("span", {"xiaoquInfoContent"})
            key_info = key_type[key.get_text().strip()]
            value_info = value.get_text().strip()
            res.update({key_info: value_info})

        except:
            continue
    return res


def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logging.error("Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False


def log_progress(function, address, page, total):
    logging.info("Progress: %s %s: current page %d total pages %d" % (function, address, page, total))
