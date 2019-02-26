#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: SenLian_ReadJson.py

@time: 2018/9/20 11:00

@module:python -m pip install 

@desc:
'''
import json, codecs
from types import *


class JsonObj(dict):
    def __init__(self, jsonFile="../startApp.json"):
        self.jsonFile = jsonFile
        super(JsonObj, self).__init__(json.loads(open(self.jsonFile, 'r').read().replace('\\', '/')))

    @property
    def Filters(self):
        return self.GetFilter(self)

    def GetFilter(self, jsonObj=None, filterList=[]):
        for key in jsonObj.keys():
            subJsonObj = jsonObj[key]
            if isinstance(subJsonObj, dict):
                curFilter = subJsonObj.get('filter', "")
                filterList.extend(curFilter if type(curFilter) is list else [curFilter])
                self.GetFilter(subJsonObj, filterList)
        filterList = map(lambda item: item.lower() if item else '', set(filterList))
        return [item for item in filterList if item]

    def SaveToFile(self):
        with codecs.open("../startApp1.json", "w", encoding="utf-8") as f:
            json.dump(self, f, ensure_ascii=False, indent=2)

    def has_obj(self, obj):
        if not isinstance(obj, dict):
            return False
        return self.IsChild(self, obj)

    def IsChild(self, parent, obj={}):
        if not isinstance(obj, dict):
            return False
        for key in obj.keys():
            if not parent.has_key(key):
                return False
            if isinstance(obj[key], dict):
                if not self.IsChild(parent[key], obj[key]):
                    return False
        return True


if __name__ == '__main__':
    print json.dumps(JsonObj(), ensure_ascii=False, indent=2)
    print JsonObj().has_obj({"ReCharge": "RechargeDbServer"})
