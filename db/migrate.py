#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from peewee_migrate import Router
from db import models
from config import settings


def makemigrate(model, ignore=['basemodel'], name='auto'):
    # if models.db.is_closed():
    #     models.db.connect()
    with model.db.atomic():
        router = Router(model.db, ignore=ignore, migrate_dir=os.path.join(settings.ROOT_DIR, 'db', 'migrations'))
        router.create(name=name, auto=model)
        router.run()
    # if not models.db.is_closed():
    #     models.db.close()


if __name__ == '__main__':
    makemigrate(models)
