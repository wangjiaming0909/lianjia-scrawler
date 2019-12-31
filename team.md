因为 云健本地没有数据，
佳明和我有比较全的小区信息，佳明本地还有 昌平的house 信息。


建议：

分区爬取，再合并：
这些是北京所有的区，原来的缺少 tongzhou， yanqing， mentougou， yizhuangkaifaqu， fangshan
newList = [u'tongzhou,u'shijingshan',u'huairou',u'miyun',u'changping',u'pinggu',u'daxing',u'yanqing,u'mentougou,u'fangshan,u'yizhuangkaifaqu,u'chaoyang',u'haidian',u'xichen',u'dongcheng',u'shunyi',u'fengtai']

现在大家都新建个数据库： 本地和原来的区分开就好
命令： 
****
create database bj
settings.py 中： DBNAME 改为 bj 
****
云健的区是: 我们缺少的这5个:

[u'tongzhou, u'yanqing, u'mentougou, u'yizhuangkaifaqu, u'fangshan]


佳明： 
[u'chaoyang',u'haidian',u'xichen',u'dongcheng',u'shunyi',u'fengtai']


我:
[u'shijingshan',u'huairou',u'miyun',u'changping',u'pinggu',u'daxing']

大家新建完数据库后， 来到setting.py 里，替换 REGIONLIST 的值为你的给定的值，之后，开始运行程序。

python scrawl.py 

我们都完事了，之后导出文件，再整合，写入到各自的数据库和服务器的数据库。