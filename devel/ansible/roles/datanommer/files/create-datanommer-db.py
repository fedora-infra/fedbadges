#!/usr/bin/env python3

import datanommer.models as dm

dm.init(
    "postgresql://datanommer:datanommer@localhost/messages",
    alembic_ini="/home/vagrant/alembic-datanommer.ini",
    create=True,
)
