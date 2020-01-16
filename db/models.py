#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# peewee文档：http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart

import os
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

from config import settings

db = SqliteExtDatabase(database=settings.SQLLITE3,
                       pragmas={'journal_mode': 'wal', 'foreign_keys': 'ON'})
__path__ = ['.']
__all__ = ['db', 'ProcessType', 'ProcessList', 'ProcessArgs']


class BaseModel(peewee.Model):
    class Meta:
        database = db


class ProcessType(BaseModel):
    '''
        0 = 日志转存
        1 = 平台
        2 = 游戏
    '''
    type_id = peewee.IntegerField(verbose_name='id', default=2, unique=True, primary_key=True, null=False, index=True)
    type_name = peewee.CharField(verbose_name='类型名', max_length=200, unique=True)
    dirpath = peewee.CharField(max_length=300, unique=True, null=False, verbose_name='进程路径')
    level = peewee.IntegerField(verbose_name='优先级', default=0, unique=True)

    class Meta:
        table_name = 'process_type'


class ProcessList(BaseModel):
    '''
        # RESTRICT（限制外表中的外键改动）
        # CASCADE（跟随外键改动）
        # SET NULL（设空值）
        # SET DEFAULT（设默认值）
        # NO ACTION（无动作，默认的）
    '''
    type = peewee.ForeignKeyField(model=ProcessType, on_delete='CASCADE', on_update='CASCADE',
                                  related_name='process', verbose_name='进程类型')
    alias = peewee.CharField(max_length=200, unique=False, null=True, verbose_name='别名')
    exe = peewee.CharField(max_length=200, unique=False, index=True, verbose_name='进程名')
    dirpath = peewee.CharField(max_length=300, unique=False, verbose_name='进程路径')

    # pid = peewee.IntegerField(default=-1, verbose_name='PID')
    # port = peewee.IntegerField(default=-1, verbose_name='端口')
    priority = peewee.IntegerField(verbose_name='启动顺序', default=99999)
    intro = peewee.TextField(null=True, verbose_name='备注')

    class Meta:
        table_name = 'process_list'
        indexes = (
            'type',
            (('type', 'priority'), True),
            (('exe', 'dirpath'), True),
        )
        # 复合主键不能作为外键使用, 采用默认生成的自增主键id
        # primary_key = peewee.CompositeKey('type', 'exe', 'dirpath')


class ProcessArgs(BaseModel):
    process = peewee.ForeignKeyField(model=ProcessList, on_delete='CASCADE', on_update='CASCADE',
                                     related_name='args', verbose_name='进程')
    exe = peewee.CharField(max_length=200, unique=False, null=True, verbose_name='进程名')
    parameter = peewee.CharField(max_length=500, default=None, null=True, verbose_name='上线参数')
    pid = peewee.IntegerField(unique=False, null=True, verbose_name='Pid')
    port = peewee.IntegerField(unique=False, null=True, verbose_name='端口号')
    # 状态：{0: '关服', -1: '下架', 1: '开服'}
    status = peewee.IntegerField(verbose_name='状态', default=0)

    class Meta:
        table_name = 'process_args'
        indexes = (
            (('process', 'exe', 'parameter'), True),
            (('parameter', 'pid'), True),
            (('parameter', 'port'), True)
        )
