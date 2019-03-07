[TOC]

# 1. 数据准备

## 1.1 数据爬取

选的是寻医问药网作为爬取对象，一开始爬了以下10个内容：

1. 简介：<http://jib.xywy.com/il_sii/gaishu/1.htm>
2. 病因：http://jib.xywy.com/il_sii/cause/1.htm
3. 预防：http://jib.xywy.com/il_sii/prevent/1.htm
4. 症状：<http://jib.xywy.com/il_sii/symptom/1.htm>
5. 并发症：http://jib.xywy.com/il_sii/neopathy/1.htm
6. 常规检查：http://jib.xywy.com/il_sii/inspect/1.htm
7. 治疗：http://jib.xywy.com/il_sii/treat/1.htm 
8. 饮食保健：[http://jib.xywy.com/il_sii/food/1.htm](http://jib.xywy.com/il_sii/food/%s.htm)
9. 好评药品：<http://jib.xywy.com/il_sii/drug/1.htm> 
10. 项目检查：<http://jck.xywy.com/jc_1.html>

前9项放在MongoDB的medical.data中，爬了5个小时，爬了4666条，显示如下：

![img](https://github.com/geyixin/MedicalKG/blob/master/picture/medical_data.png)

第10项放在MongoDB的medical.jc中，存储的常规检查的连接、名字以及介绍，爬了1个小时，爬了3660条：

![img](https://github.com/geyixin/MedicalKG/blob/master/picture/medical_jc.png)

## 1.2. 数据预处理

- 爬取的数据简单处理成便于操作的形式：直接通过key即可实现索引。这样后面导成json格式的才方便neo4j使用。处理好的数据放在medical.medical中3371条。

![img](https://github.com/geyixin/MedicalKG/blob/master/picture/medical_medical.png)

**medical库中数据显示如下：**

![img](https://github.com/geyixin/MedicalKG/blob/master/picture/medical.png)

**先将medical.medical数据从MongoDB导出，导成json格式：**

 **.\mongoexport** **-d** **dbtest** **-c** **collection** **-o** **E:\tmp.json**

**然后按照下面的"2.知识图谱构建"把json格式的数据在neo4j中构建成知识图谱。**

# 2.知识图谱构建

## 2.1 实体构建，7类：疾病，药品，食物，检查，科室，药品生产者，症状

- 疾病实体标签定为：Disease，属性包括：name，desc(描述)，prevent，cause，easy_get(患病概率)，cure_lasttime，cure_department，cure_way，cured_prob。

- ```python
  from py2neo import Node self.g = Graph(host="127.0.0.1",http_port=7474,user="neo4j", password="123456") 
  node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'], prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],             cure_department=disease_dict['cure_department'], cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
  self.g.create(node) 
  ```

- 其余6个实体属性：name。对应标签依次为：：Drug、Food、Check、Department、Producer、Symptom

- ```python
  node = Node(label, name=node_name) self.g.create(node) 
  ```

## 2.2 关系构建，11类：

- 疾病-推荐食谱、疾病-忌吃、疾病-宜吃、科室-科室、疾病-常用用品、生产商-药品、疾病-好评药品、疾病-检查、疾病-症状、疾病-并发症、疾病-科室

- ```python
  # 写一个CQL语句去创建实体间的关系 
  query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, p, q, rel_type, rel_name)
  self.g.run(query) 
  ```

  注意：**3. 自动问答** **运行之前要保证neo4j处于已连接状态！**

# 3. 自动问答

## 3.1 问句分类

1. 获取问句中的属于7大实体中的词；
2. 获取question_types，例如：disease_cause、disease_acompany；

- 如果问：感冒忌吃什么，返回的内容为：{'args': {'感冒': ['disease']}, 'question_types': ['disease_not_food']}
- 如果问：感冒是什么，返回内容为：{'args': {'感冒': ['disease']}, 'question_types': ['disease_desc']}

## 3.2 问句解析

1. 根据上一部分返回的类似：{'args': {'感冒': ['disease']}, 'question_types': ['disease_not_food']}的内容，分别获取其'args'内容（也就是实体）和 'question_types'；
2. 根据获取的'args'和'question_types'生成CQL语句；

## 3.3 查询

1. 执行上一部分返回的CQL语句，并获取执行结果：ress = self.g.run(query).data()，返回的ress类似：

- ```
  [
  {'m.name': '感冒', 'r.name': '忌吃', 'n.name': '白扁豆'},
  {'m.name': '感冒', 'r.name': '忌吃', 'n.name': '猪油（板油）'}, 
  {'m.name': '感冒', 'r.name': '忌吃', 'n.name': '油条'}, 
  {'m.name': '感冒', 'r.name': '忌吃', 'n.name': '咸鱼'}
  ]
  ```

2. 提取对应的'n.name'，整理成易读的形式返回，比如：感冒忌食的食物包括有：白扁豆；咸鱼；油条；猪油（板油）


**运行的效果类似这样：**
![运行效果图](https://github.com/geyixin/MedicalKG/blob/master/picture/run.png)
