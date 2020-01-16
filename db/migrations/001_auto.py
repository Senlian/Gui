"""Peewee migrations -- 001_auto.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw
from decimal import ROUND_HALF_EVEN

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class ProcessType(pw.Model):
        type_id = pw.IntegerField(constraints=[SQL("DEFAULT 2")], primary_key=True)
        type_name = pw.CharField(max_length=200, unique=True)
        dirpath = pw.CharField(max_length=300, unique=True)
        level = pw.IntegerField(constraints=[SQL("DEFAULT 0")], unique=True)

        class Meta:
            table_name = "process_type"

    @migrator.create_model
    class ProcessList(pw.Model):
        id = pw.AutoField()
        type = pw.ForeignKeyField(backref='process', column_name='type_id', field='type_id', model=migrator.orm['process_type'], on_delete='CASCADE', on_update='CASCADE')
        alias = pw.CharField(max_length=200, null=True)
        exe = pw.CharField(index=True, max_length=200)
        dirpath = pw.CharField(max_length=300)
        priority = pw.IntegerField(constraints=[SQL("DEFAULT 99999")])
        intro = pw.TextField(null=True)

        class Meta:
            table_name = "process_list"
            indexes = ['type', (('type', 'priority'), True), (('exe', 'dirpath'), True)]

    @migrator.create_model
    class ProcessArgs(pw.Model):
        id = pw.AutoField()
        process = pw.ForeignKeyField(backref='args', column_name='process_id', field='id', model=migrator.orm['process_list'], on_delete='CASCADE', on_update='CASCADE')
        exe = pw.CharField(max_length=200, null=True)
        parameter = pw.CharField(max_length=500, null=True)
        pid = pw.IntegerField(null=True, unique=True)
        port = pw.IntegerField(null=True, unique=True)
        status = pw.IntegerField(constraints=[SQL("DEFAULT 0")])

        class Meta:
            table_name = "process_args"
            indexes = [(('process', 'exe', 'parameter'), True), (('parameter', 'pid'), True), (('parameter', 'port'), True), (('pid', 'port'), True)]



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('process_args')

    migrator.remove_model('process_list')

    migrator.remove_model('process_type')