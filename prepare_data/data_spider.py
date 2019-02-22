#!/usr/bin/env python3
# coding: utf-8

import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

'''基于司法网的犯罪案件采集'''
class CrimeSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient()
        self.db = self.conn['medical']
        self.col = self.db['data']

    '''根据url，请求html'''
    def get_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('gbk')
        return html

    '''url解析'''
    def url_parser(self, content):
        selector = etree.HTML(content)
        urls = ['http://www.anliguan.com' + i for i in selector.xpath('//h2[@class="item-title"]/a/@href')]
        return urls

    '''测试'''
    def spider_main(self):
        for page in range(1, 11000):
        # for page in range(1, 10):
            try:
                basic_url = 'http://jib.xywy.com/il_sii/gaishu/%s.htm'%page
                cause_url = 'http://jib.xywy.com/il_sii/cause/%s.htm'%page
                prevent_url = 'http://jib.xywy.com/il_sii/prevent/%s.htm'%page
                neopathy_url = 'http://jib.xywy.com/il_sii/neopathy/%s.htm'%page
                symptom_url = 'http://jib.xywy.com/il_sii/symptom/%s.htm'%page
                inspect_url = 'http://jib.xywy.com/il_sii/inspect/%s.htm'%page
                treat_url = 'http://jib.xywy.com/il_sii/treat/%s.htm'%page
                food_url = 'http://jib.xywy.com/il_sii/food/%s.htm'%page
                drug_url = 'http://jib.xywy.com/il_sii/drug/%s.htm'%page
                data = {}
                data['url'] = basic_url
                data['basic_info'] = self.basicinfo_spider(basic_url)
                data['cause_info'] =  self.common_spider(cause_url)
                data['prevent_info'] =  self.common_spider(prevent_url)
                data['neopathy_info'] =  self.neopathy_spider(neopathy_url)
                data['symptom_info'] = self.symptom_spider(symptom_url)
                data['inspect_info'] = self.inspect_spider(inspect_url)
                data['treat_info'] = self.treat_spider(treat_url)
                data['food_info'] = self.food_spider(food_url)
                data['drug_info'] = self.drug_spider(drug_url)
                # print(type(data['neopathy_info']), type(data['drug_info']))
                print(page, basic_url)
                self.col.insert(data)

            except Exception as e:
                print(e, page)
        return

    '''基本信息解析'''
    def basicinfo_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0]     # 疾病名称
        category = selector.xpath('//div[@class="wrap mt10 nav-bar"]/a/text()')     # 种类
        desc = selector.xpath('//div[@class="jib-articl-con jib-lh-articl"]/p/text()')  # 描述
        ps = selector.xpath('//div[@class="mt20 articl-know"]/p')
        # 想获取多个<div class="mt20 articl-know">的<p></p>中的内容，再配合xpath('string(.)')即可
        infobox = []
        for p in ps:
            # \r:回车,\n：换行,\xa0:不间断空格,\t：横向制表符
            # 注意：xpath中的 string 与 text 区别！
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infobox.append(info)
        basic_data = {}
        basic_data['category'] = category
        basic_data['name'] = title.split('的简介')[0]
        basic_data['desc'] = desc
        basic_data['attributes'] = infobox
        return basic_data

    '''并发症 解析'''        # 新加 By gyx
    def neopathy_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        neopathy = selector.xpath('//a[@class="gre mr15"]/text()')
        return neopathy

    '''treat_infobox治疗解析'''
    def treat_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')  # starts-with 是xpath的用来匹配的方法之一
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infobox.append(info)
        return infobox

    '''treat_infobox治疗解析'''
    def drug_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]
        return drugs

    '''food治疗解析'''
    def food_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        divs = selector.xpath('//div[@class="diet-img clearfix mt20"]')
        try:
            food_data = {}
            food_data['good'] = divs[0].xpath('./div/p/text()')
            food_data['bad'] = divs[1].xpath('./div/p/text()')
            food_data['recommand'] = divs[2].xpath('./div/p/text()')
        except:
            return {}

        return food_data

    '''症状信息解析'''
    def symptom_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        symptoms = selector.xpath('//span[@class="db f12 lh240 mb15 "]/a/text()')
        ps = selector.xpath('//p')
        detail = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            detail.append(info)
        symptoms_data = {}
        symptoms_data['symptoms'] = symptoms
        symptoms_data['symptoms_detail'] = detail
        return symptoms, detail

    '''检查信息解析'''
    def inspect_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        inspects  = selector.xpath('//li[@class="check-item"]/a/@href')
        return inspects

    '''通用解析模块'''
    def common_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ','').replace('\t', '')
            if info:
                infobox.append(info)
        return '\n'.join(infobox)

    def inspect_crawl2(self):
        for page in range(1, 3685):
            try:
                url = 'http://jck.xywy.com/jc_%s.html'%page
                html = self.get_html(url)
                data = {}
                data['url']= url
                selector = etree.HTML(html)
                data['name'] = selector.xpath('//title/text()')[0].split('结果分析')[0]  # 检查名字
                data['desc'] = selector.xpath('//meta[@name="description"]/@content')[0].replace('\r\n\t', '')  # 描述
                print(url)
                self.db['jc'].insert(data)
            except Exception as e:
                print(e)


handler = CrimeSpider()
# handler.spider_main()
handler.inspect_crawl2()