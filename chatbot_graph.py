#!/usr/bin/env python3
# coding: utf-8

from question_classifier import *
from question_parser import *
from answer_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好'
        res_classify = self.classifier.classify(sent)
        # print(res_classify)     # {'args': {'感冒': ['disease']}, 'question_types': ['disease_not_food']}
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        # print(res_sql)  # [{'question_type': 'disease_not_food', 'sql': ["MATCH (m:Disease)-[r:no_eat]->(n:Food) where m.name = '感冒' return m.name, r.name, n.name"]}]
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('用户:')     # 感冒忌吃什么
        answer = handler.chat_main(question)
        print('AI:', answer)

