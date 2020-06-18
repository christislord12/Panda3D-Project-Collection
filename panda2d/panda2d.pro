TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG -= qt

SOURCES +=

include(deployment.pri)
qtcAddDeployment()

DISTFILES += \
    main_m.py \
    panda2d/other_tiles.py \
    panda2d/xmlDao.py \
    panda2d/world.py \
    panda2d/tiles.py \
    panda2d/__init__.py \
    panda2d/sprites.py \
    m/models.py \
    m/__init__.py \
    m/main.py \
    panda2d/new_other_tiles.py \
    m/data/l1.tmx

