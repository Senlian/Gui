#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from peewee_migrate import Router
from db import models


def makemigrate(model, ignore=['basemodel'], name='auto'):
    # if models.db.is_closed():
    #     models.db.connect()
    with model.db.atomic():
        router = Router(model.db, ignore=ignore, migrate_dir=os.path.join(model.curDir, 'migrations'))
        router.create(name=name, auto=model)
        router.run()
    # if not models.db.is_closed():
    #     models.db.close()


if __name__ == '__main__':
    makemigrate(models)