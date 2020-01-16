#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from db.models import db, ProcessList, ProcessArgs


class ReadSqlDB(object):
    def __init__(self, model, index_col=None):
        self.sql = pd.read_sql('SELECT * FROM %s' % model._meta.table_name, db, index_col=index_col)

    def export_type(self, excel_writer):
        self.sql.to_excel(excel_writer=excel_writer, sheet_name='Sheet1', index=False)
        if isinstance(excel_writer, pd.ExcelWriter):
            excel_writer.save()

    def export_process(self, excel_writer):
        self.args = pd.read_sql('SELECT * FROM %s' % ProcessArgs._meta.table_name, db, index_col='id')
        if not self.args.empty:
            self.args.fillna('', inplace=True)
            self.args = self.args.groupby(by=['process_id', 'exe', 'status'])['parameter'].apply(
                lambda x: x.values.tolist()).reset_index()
            # self.args = self.args.groupby(by=['process_id', 'exe', 'status'])['parameter'].apply(
            #     lambda x: print(x.to_dict())).reset_index()
            # print(self.args)
            df = self.sql.merge(right=self.args.loc[:, ['process_id', 'status', 'parameter']],
                                left_on='id', right_on='process_id', how='outer')
        else:
            df = self.sql
            df['parameter'] = pd.Series([])
            df['status'] = -1

        df.fillna('', inplace=True)
        df['intro'].replace(to_replace='nan', value='', inplace=True)
        df = df.loc[:, ['type_id', 'alias', 'dirpath', 'exe', 'priority', 'parameter', 'status', 'intro']]
        df.to_excel(excel_writer=excel_writer, sheet_name='Sheet2', index=False)
        if isinstance(excel_writer, pd.ExcelWriter):
            excel_writer.save()

    def get_process(self):
        self.args = pd.read_sql('SELECT * FROM %s' % ProcessArgs._meta.table_name, db)
        df = self.sql.merge(right=self.args.loc[:, ['id', 'process_id', 'parameter', 'pid', 'port', 'status']],
                            left_on='id', right_on='process_id', how='outer')
        df['id'].fillna('-1', inplace=True)
        df['status'].fillna('-1', inplace=True)
        df['pid'].fillna('-1', inplace=True)
        df['port'].fillna('-1', inplace=True)

        df['id'] = df['id'].astype(int)
        df['pid'] = df['pid'].astype(int)
        df['port'] = df['port'].astype(int)
        df['status'] = df['status'].astype(int)

        df.fillna('', inplace=True)
        df['intro'].replace(to_replace='nan', value='', inplace=True)
        df['sort'] = df['type_id'].map(lambda x: int(x) * 1000000) + \
                     df['priority'].map(lambda x: int(x) * 100000) - \
                     df['status'].map(lambda x: int(x) * 90000000 if int(x) < 0 else 0) + \
                     df['parameter'].map(lambda x: 0 if not str(x).isdigit() else int(x))

        df.sort_values(['sort'], inplace=True, ascending=True)
        # df.sort_values(['type_id', 'priority'], inplace=True, ascending=True)

        df.reset_index(drop=True, inplace=True)
        return df

    def get_types(self):
        self.sql.sort_values(['level'], inplace=True)
        return self.sql


if __name__ == '__main__':
    # excel_writer = pd.ExcelWriter(path='dd.xlsx')
    # r = ReadSqlDB(ProcessList)
    # r.export_type(excel_writer)
    # df = r.export_process(excel_writer)
    # print(df.loc[:,['exe', 'parameter']])

    r = ReadSqlDB(ProcessList, index_col='id')
    df = r.get_process()
    print(df)
    print(df['status'].apply(int))
    print(df.applymap(str)[['exe', 'pid']])
