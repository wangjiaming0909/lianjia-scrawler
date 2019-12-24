from model import Houseinfo
from model import Hisprice
import model
import datetime


def getCheapestHousesOfCommunity(communityID, n):
    ### get cheapest [n] houses in community [communityID]
    houses = Houseinfo.select() \
        .where(Houseinfo.communityID == communityID) \
        .order_by(Houseinfo.totalPrice.asc()).limit(n)
    return houses


def getPriceChangeHousesOfCommunity(communityID, daysBefore):
    ### get houses which cut the price [daysBefore] days before in community [CommunityID]
    todayDate = datetime.datetime.today().date()
    deltaDay = datetime.timedelta(days=daysBefore)
    startDate = todayDate - deltaDay
    #cte = Hisprice.select(Hisprice.houseID,
    #                      model.fn.MIN(Hisprice.totalPrice).alias('minPrice'),
    #                      model.fn.MAX(Hisprice.totalPrice).alias('maxPrice')).where(
    #    Hisprice.date >= startDate).group_by(Hisprice.houseID).having(
    #    model.fn.COUNT(Hisprice.id) > 1).cte('t', columns=('houseID', 'minPrice', 'maxPrice'))
    #houses = Houseinfo.select().join(cte, on=(Houseinfo.houseID == cte.c.houseID))

    sqlQuery = \
    "select * from \
        (select * from\
	        (select houseID,\
	        first_value(totalPrice) over (partition by houseID order by date asc) as fp,\
	        last_value(totalPrice) over (partition by houseID order by date asc) as lp\
	        FROM hisprice\
	    WHERE date >= {})t\
    where lp != fp)tt left join houseinfo on houseinfo.houseID = tt.houseID".format(str(startDate))

    cursor = model.database.execute_sql(sqlQuery)
    return cursor


def getPriceUpHousesOfCommunity(communityID, daysBefore):
    pass


if __name__ == '__main__':
    houses = getCheapestHousesOfCommunity('1111027381003', 10)
    for house in houses:
        print(house.houseID, house.communityID, house.totalPrice)

    houses = getPriceChangeHousesOfCommunity('1111027381003', 3)
    for house in houses:
        for i in range(len(house)):
            print(house[i], end=' ')

        print()
