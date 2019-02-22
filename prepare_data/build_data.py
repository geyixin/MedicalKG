#!/usr/bin/env python3
# coding: utf-8


import pymongo
from lxml import etree
import os
from max_cut import *

class MedicalGraph:
    def __init__(self):
        self.conn = pymongo.MongoClient()
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.db = self.conn['medical']
        self.col = self.db['data']
        self.key_dict = {
            '医保疾病' : 'yibao_status',
            "患病比例" : "get_prob",
            "易感人群" : "easy_get",
            "传染方式" : "get_way",
            "就诊科室" : "cure_department",
            "治疗方式" : "cure_way",
            "治疗周期" : "cure_lasttime",
            "治愈率" : "cured_prob",
            '药品明细': 'drug_detail',
            '药品推荐': 'recommand_drug',
            '推荐': 'recommand_eat',
            '忌食': 'not_eat',
            '宜食': 'do_eat',
            '症状': 'symptom',
            '检查': 'check',
            '成因': 'cause',
            '预防措施': 'prevent',
            '所属类别': 'category',
            '简介': 'desc',
            '名称': 'name',
            '常用药品' : 'common_drug',
            '治疗费用': 'cost_money',
            '并发症': 'acompany'
        }
        self.cuter = CutWords()

    def collect_medical(self):
        cates = []
        inspects = []
        count = 0
        for item in self.col.find():
            data = {}
            basic_info = item['basic_info']
            name = basic_info['name']
            if not name:    # data_spider.py爬取了11000个页面，其中靠后的可能没有东西
                continue
            # 基本信息
            data['名称'] = name
            data['简介'] = '\n'.join(basic_info['desc']).replace('\r\n\t', '').replace('\r\n\n\n','').replace(' ','').replace('\r\n','\n')
            category = basic_info['category']
            data['所属类别'] = category
            cates += category
            inspect = item['inspect_info']  # 链接
            inspects += inspect
            attributes = basic_info['attributes']

            # 成因及预防
            data['预防措施'] = item['prevent_info']
            data['成因'] = item['cause_info']

            # 症状
            data['症状'] = list(set([i for i in item["symptom_info"][0]]))

            # 并发症
            data['并发症'] = item["neopathy_info"]     # 新加 By gyx

            # attributes
            for attr in attributes:
                attr_pair = attr.split('：')
                if len(attr_pair) == 2:     # 舍弃最后的“温馨提示”
                    key = attr_pair[0]
                    value = attr_pair[1]
                    if key != "并发症": 
                        data[key] = value # 医保疾病、患病比例、易感人群、传染方式、并发症、就诊科室、治疗方式、治疗周期、治愈率、常用药品、治疗费用

            # 检查
            inspects = item['inspect_info']     # 之前爬下来的是各种常规检查的链接
            jcs = []
            for inspect in inspects:
                jc_name = self.get_inspect(inspect)
                if jc_name:
                    jcs.append(jc_name)
            data['检查'] = jcs

            # 食物
            food_info = item['food_info']
            if food_info:
                data['宜食'] = food_info['good']
                data['忌食'] = food_info['bad']
                data['推荐'] = food_info['recommand'] # 推荐食谱

            # 药品
            drug_info = item['drug_info']   # 好评药品
            data['药品推荐'] = list(set([i.split('(')[-1].replace(')','') for i in drug_info])) # 无重复的取括号中的内容
            data['药品明细'] = drug_info

            data_modify = {}

            for attr, value in data.items():
                attr_en = self.key_dict.get(attr)
                if attr_en:
                    data_modify[attr_en] = value
                if attr_en in ['yibao_status', 'get_prob', 'easy_get', 'get_way', "cure_lasttime", "cured_prob"]:
                    data_modify[attr_en] = value.replace(' ','').replace('\t','')
                elif attr_en in ['cure_department', 'cure_way', 'common_drug']:
                    data_modify[attr_en] = [i for i in value.split(' ') if i]

            try:
                self.db['medical'].insert(data_modify)
                count += 1
                print(count)
            except Exception as e:
                print(e)

        return

    def get_inspect(self, url):
        res = self.db['jc'].find_one({'url':url})
        if not res:
            return ''
        else:
            return res['name']


if __name__ == '__main__':
    handler = MedicalGraph()
    handler.collect_medical()
