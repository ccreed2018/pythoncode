import requests
import json
from time import time
from lxml import etree
import re
from random import sample
from time import sleep

np = 1
base = "http://fund.eastmoney.com/"
acount = 2
# 爬取排行页
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4620.400 QQBrowser/9.7.13014.400'
}
url = "http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&sd=2017-07-09&ed=2018-07-09&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1&v=0."


def IndexSpider(url, headers):  # 爬取第一个页面信息
    url = url + str(int(time()))  # 这个主要是url最后一个值是v=数字，我就用时间戳来伪装了
    rsp = requests.get(url, headers=headers).content
    html = rsp.decode('utf-8')
    url = url[:-10]  # 请求完了之后减掉加的时间戳，方面爬取下一页的时候重复操作
    return html


def ChangeUrl(url):  # 改变url，pi代表的是页数，这样可以按顺序爬取相应页数的数据
    global acount
    url = url.replace("&pi=1", "&pi=" + str(acount))
    acount = acount + 1
    return url


def ChangeUrl_2(jijindaima):  # 我要爬取相应基金点开之后的页面的数据，分析可知是对应基金代码前面加上域名，后面加上.html
    global base
    jijindaima = jijindaima.replace('\"', '')
    url_2 = base + jijindaima + '.html'
    return url_2


def DetailRequest(url):  # 爬取点开那一页之后的数据
    global np
    url = url.replace('\"', '')
    print(url)
    print("正在爬取第{0}条记录".format(np))
    np = np + 1
    re_leixing = re.compile('基金类型(.*?)</a>')
    re_jingli = re.compile('基金经理：<a href=(.*?)</a>')
    re_chengliri = re.compile('<td><span class="letterSpace01">成 立 日</span>：(.*?)</td>')
    rsp = requests.get(url, headers=headers).content
    html = rsp.decode('utf-8')
    leixing = re_leixing.findall(html)[0][-3:]
    jingli = re_jingli.findall(html)[0][-2:]
    chengliri = re_chengliri.findall(html)[0]
    return jingli, leixing, chengliri


if __name__ == '__main__':
    nw = 1
    url2_detail = []
    jijindaima_list = []
    detail_url_list = []
    with open('w.txt', 'a', encoding='utf-8') as f:
        f.write("基金代码\t\t基金简称\t\t单位净值\t\t累计净值\t\t基金经理\t\t基金类型\t\t成立日\n")
    for i in range(1, 32):
        html = IndexSpider(url, headers=headers)
        url = ChangeUrl(url)
        right = html.find("]")
        left = html.find("[")
        html = html[left + 1:right]
        lists = html.split("\",\"")
        for list in lists:
            l = list.split(",")
            jijindaima_list.append(l[0])
        for i in jijindaima_list:
            detail_url_list.append(ChangeUrl_2(i))
        for i in detail_url_list:
            url2_detail.append(DetailRequest(i))
        with open('w.txt', 'a', encoding='utf-8') as f:
            for list, l2 in zip(lists, url2_detail):
                l = list.split(",")
                f.writelines(
                    l[0] + '\t\t' + l[1] + '\t\t' + l[4] + '\t\t' + l[5] + '\t\t' + l2[0] + '\t\t' + l2[1] + '\t\t' +
                    l2[2] + '\n')
                print('正在写入第{0}条记录……'.format(nw))
                nw = nw + 1
        print("5秒后爬取下一页……")
        sleep(5)