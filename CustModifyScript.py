#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: CustModifyScript.py

@time: 2018/7/31 9:38

@module:python -m pip install 

@desc:
'''
import os, re, shutil, time, socket, urllib, csv
from bs4 import BeautifulSoup
from threading import Thread

def get_host_ip():
    return socket.gethostbyname_ex(socket.gethostname())[2][0]


def get_host_ip_ex():
    try:
        url = urllib.urlopen('https://ip.cn/')
        content = url.read()
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf8')
        return soup.find('div', attrs={'id': 'cf-error-details'}).find('div', attrs={'class': 'cf-error-footer'}).find(
                'p').findAll('span')[2].get_text().split('Your IP:')[1].replace(' ', '')
    except:
        return None

class MyThread(Thread):
    def __init__(self, parent=None):
        super(MyThread, self).__init__()
        self.LeftTree = parent.LeftTree
        self.RightText = parent.RightText
        self.FileList = parent.FileList
        self.root = parent.root
        self.ServiceNames = parent.ServiceNames
        self.start()

    def run(self):
        csvObj = None
        csvOldF = None
        for curFile in self.FileList:
            self.LeftTree.CollapseTree()
            self.LeftTree.ExpandPath(os.path.abspath(curFile))
            subDir = os.path.basename(os.path.dirname(curFile))
            if not (re.findall(r'^[\d_]+$', subDir)):
                continue
            GameID = subDir.split('_')[0]
            if curFile.endswith(str(os.path.basename(self.root.FreeTemplate))):
                Template = self.root.FreeTemplate
                defaultName = u'[自由]游戏服'
                csvFile = os.path.abspath('./GameList.csv')
            elif curFile.endswith(str(os.path.basename(self.root.GroupTemplate))):
                Template = self.root.GroupTemplate
                defaultName = u'[组队]游戏服'
                csvFile = os.path.abspath('./GroupList.csv')
            else:
                Template = None
                continue

            if not Template:
                return False
            if csvOldF != csvFile:
                if os.path.isfile(csvFile):
                    newFileName = os.path.splitext(os.path.basename(csvFile))[0] + time.strftime('_%Y%m%d%H%M%S') + \
                                  os.path.splitext(os.path.basename(csvFile))[1]
                    if not os.path.isdir(self.root.BackPath):
                        os.makedirs(self.root.BackPath)
                    dstFile = os.path.normpath(os.path.join(self.root.BackPath, newFileName))
                    shutil.move(csvFile, dstFile)
                csvFP = open(csvFile, 'w')
                csvObj = csv.writer(csvFP)
                csvObj.writerow(['Dir', 'GameID', 'ServicePort', 'ServerID'])
                csvOldF = csvFile
            else:
                csvFP = open(csvFile, 'a')
                csvObj = csv.writer(csvFP)

            LocalTemplate = DeployConfigure(Template)
            ServiceName = self.ServiceNames.get(subDir, defaultName)

            for sec in LocalTemplate.sections:
                for opt in LocalTemplate.get_options(sec):
                    value = LocalTemplate.get_value(sec, opt)
                    if re.findall('^GameID$', value, re.IGNORECASE):
                        value = GameID
                    if re.findall('^ServiceName$', value, re.IGNORECASE):
                        value = ServiceName
                    if re.findall('^IP\*$', value, re.IGNORECASE):
                        value = get_host_ip_ex()
                    if re.findall('^IP$', value, re.IGNORECASE):
                        value = get_host_ip()
                    if re.findall('^\d+\+$', value):
                        var = locals().get(sec + '_' + opt, None)
                        if not var:
                            var = int(value[0:-1])
                            locals().update({sec + '_' + opt: var})
                        else:
                            locals().update({sec + '_' + opt: int(var) + 1})
                        var = locals().get(sec + '_' + opt, None)
                        value = str(var)
                    LocalTemplate.set_value(sec, opt, str(value.encode('utf-8')))
            csvObj.writerow([subDir, GameID,
                             locals().get('GroupServer_ServicePort', locals().get('GameServer_ServicePort', 0)),
                             locals().get('GroupServer_ServerID', 0)])
            csvFP.close()
            LocalTemplate.save(curFile)


if __name__ == '__main__':
    pass
