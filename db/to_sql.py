#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ast
import numpy as np
import pandas as pd
from db.models import db, ProcessType, ProcessArgs, ProcessList

curDir = os.path.dirname(os.path.abspath(__file__))


class ToSqliteDB(object):
    @db.atomic()
    def __init__(self, excel=os.path.join(curDir, 'jqp.xlsx'), header=0, sheet_name=0):
        if not excel:
            raise TypeError('Missing excel files, please pass in !')
        self.excel = pd.read_excel(io=excel, header=header, sheet_name=sheet_name)

    def truncate(self, table=ProcessType):
        table.truncate_table()

    def update_type(self):
        columns = ['type_id', 'type_name', 'dirpath', 'level']
        return self.update(ProcessType, columns)

    def update_process(self):
        columns = ['type_id', 'alias', 'exe', 'dirpath', 'priority', 'intro']
        return self.update(ProcessList, columns)

    def prestep(self, rs):
        args = rs['parameter']
        if args is np.nan:
            rs['parameter'] = []
        elif args.strip().startswith('[') and args.strip().endswith(']'):
            rs['parameter'] = eval(args)
        else:
            rs['parameter'] = None
        return rs

    @db.atomic()
    def update_args(self):
        self.excel = self.excel.apply(self.prestep, axis=1)
        try:
            for i in self.excel.index:
                exe = ProcessList.get_or_none(
                    ProcessList.type == self.excel.loc[i, 'type_id'],
                    ProcessList.alias == self.excel.loc[i, 'alias'],
                    ProcessList.exe == self.excel.loc[i, 'exe'],
                    ProcessList.dirpath == self.excel.loc[i, 'dirpath'],
                )
                if exe:
                    args = self.excel.loc[i, ['parameter', 'status']]
                    args.fillna(-1, inplace=True)
                    if isinstance(args['parameter'], list):
                        # 注意如果excel中有两行相同进程的，此处会造成以最后一行为准
                        ProcessArgs.delete().where(ProcessArgs.process == exe).execute()
                        if not args['parameter']:
                            ProcessArgs.insert(process=exe, exe=exe.exe, status=args['status']).execute()
                        else:
                            for arg in args['parameter']:
                                ProcessArgs.insert(process=exe, exe=exe.exe, parameter=arg, status=args['status']).execute()
        except Exception as e:
            raise e
            return e
        return False

    @db.atomic()
    def update(self, model=None, columns=None, df=None):
        try:
            if not (model and columns):
                raise ValueError('Lack of the participation!')
            df = self.excel.loc[:, columns] if not df else df.loc[:, columns]

            sql = model.insert_many([df.loc[i].to_dict() for i in df.index]).on_conflict_replace()
            sql.execute()
        except Exception as e:
            raise e
            return e
        return False


if __name__ == '__main__':
    src = ToSqliteDB(sheet_name=0)
    src.update_type()
    src = ToSqliteDB(sheet_name=1)
    src.update_process()
    src.update_args()
    # dd = src.excel.loc[:, ['type_id', 'type_name', 'dirpath', 'level']]
    # src = SqliteDB(sheet_name=1)
    # src.update_process()
    # dd = src.excel.loc[:, ['type_id', 'alias', 'exe', 'dirpath', 'priority', 'status', 'intro']]
