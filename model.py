from peewee import *
import datetime
import settings

if settings.DBENGINE.lower() == 'mysql':
    database = MySQLDatabase(
        settings.DBNAME,
        host=settings.DBHOST,
        port=settings.DBPORT,
        user=settings.DBUSER,
        passwd=settings.DBPASSWORD,
        charset='utf8',
        use_unicode=True,
    )

elif settings.DBENGINE.lower() == 'sqlite3':
    database = SqliteDatabase(settings.DBNAME)

elif settings.DBENGINE.lower() == 'postgresql':
    database = PostgresqlDatabase(
        settings.DBNAME,
        user=settings.DBUSER,
        password=settings.DBPASSWORD,
        host=settings.DBHOST,
        charset='utf8',
        use_unicode=True,
    )

else:
    raise AttributeError("Please setup datatbase at settings.py")


class BaseModel(Model):
    class Meta:
        database = database


class Community(BaseModel):
    id = BigIntegerField(primary_key=True)
    title = CharField()
    link = CharField(unique=True)
    district = CharField()
    bizcircle = CharField()
    tagList = CharField()
    onsale = CharField()
    onrent = CharField(null=True)
    year = CharField(null=True)
    housetype = CharField(null=True)
    cost = CharField(null=True)
    service = CharField(null=True)
    company = CharField(null=True)
    building_num = CharField(null=True)
    house_num = CharField(null=True)
    price = CharField(null=True)
    validdate = DateTimeField(default=datetime.datetime.now)


def getAllMutableFields():
    return [Houseinfo.title, Houseinfo.link,
            Houseinfo.years, Houseinfo.housetype,
            Houseinfo.taxtype,
            Houseinfo.totalPrice, Houseinfo.unitPrice, Houseinfo.followInfo,
            Houseinfo.decoration, Houseinfo.validdate, Houseinfo.isSold]

def getAllUnmutableFieldsOfHouseInfo():
    return [Houseinfo.houseID, Houseinfo.communityID]


class Houseinfo(BaseModel):
    houseID = CharField(primary_key=True)
    title = CharField()
    link = CharField()
    communityID = CharField()
    years = CharField()
    housetype = CharField()
    square = CharField()
    direction = CharField()
    floor = CharField()
    taxtype = CharField()
    totalPrice = CharField()
    unitPrice = CharField()
    followInfo = CharField()
    decoration = CharField()
    validdate = DateTimeField(default=datetime.datetime.now)
    isSold = CharField(default='no')


class Hisprice(BaseModel):
    id = PrimaryKeyField()
    houseID = CharField()
    totalPrice = CharField()
    date = DateField(default=datetime.datetime.now().date())

    # class Meta:
    #     primary_key = CompositeKey('houseID', 'totalPrice', 'date')


class Sellinfo(BaseModel):
    houseID = ForeignKeyField(Houseinfo, Houseinfo.houseID, primary_key=True)
    title = CharField()
    link = CharField()
    community = CharField()
    years = CharField()
    housetype = CharField()
    square = CharField()
    direction = CharField()
    floor = CharField()
    status = CharField()
    source = CharField()
    totalPrice = CharField()
    unitPrice = CharField()
    dealdate = CharField(null=True)
    updatedate = DateTimeField(default=datetime.datetime.now)


class Monthsellinfo(BaseModel):
    houseID = ForeignKeyField(Houseinfo, Houseinfo.houseID, primary_key=True)
    title = CharField()
    link = CharField()
    community = CharField()
    years = CharField()
    housetype = CharField()
    square = CharField()
    direction = CharField()
    floor = CharField()
    status = CharField()
    source = CharField()
    totalPrice = CharField()
    unitPrice = CharField()
    dealdate = CharField(null=True)
    updatedate = DateTimeField(default=datetime.datetime.now)


class Rentinfo(BaseModel):
    houseID = ForeignKeyField(Houseinfo, Houseinfo.houseID, primary_key=True)
    title = CharField()
    link = CharField()
    region = CharField()
    zone = CharField()
    meters = CharField()
    other = CharField()
    subway = CharField()
    decoration = CharField()
    heating = CharField()
    price = CharField()
    pricepre = CharField()
    updatedate = DateTimeField(default=datetime.datetime.now)


def database_init():
    database.connect()
    database.create_tables([Community, Houseinfo, Hisprice, Sellinfo, Monthsellinfo, Rentinfo], safe=True)
    idx = Hisprice.index(Hisprice.houseID)
    Hisprice.add_index(idx)
    database.close()
