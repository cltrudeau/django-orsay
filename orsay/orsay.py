import os, shutil
from importlib.util import spec_from_file_location, module_from_spec

from screwdriver import DictObject

from .boot_django import boot_django
from .gallery import make_galleries

def make_album(user_config):
    ORSAY_DIR = os.path.abspath(os.path.dirname(__file__))
    ORSAY_STATIC = os.path.join(ORSAY_DIR, 'static')

    # create our global configuration object
    settings = DictObject(user_config)
    settings._src['static_path'] = os.path.relpath(settings.STATIC,
        settings.ALBUM) + '/'

    # setup the output directory
    os.makedirs(settings.ALBUM, exist_ok=True)
    static_dest = os.path.join(settings.ALBUM, 'static')
    os.makedirs(static_dest, exist_ok=True)

    # copy our static dir into the new output location
    with os.scandir(ORSAY_STATIC) as paths:
        for path in paths:
            if not path.name.startswith('.') and path.is_file():
                shutil.copy(path, static_dest)

    # copy the user's static dir into the new output location
    with os.scandir(settings.STATIC) as paths:
        for path in paths:
            if not path.name.startswith('.') and path.is_file():
                shutil.copy(path, static_dest)

    # load the user's content python file
    spec = spec_from_file_location('content', settings.CONTENT)
    content = module_from_spec(spec)
    spec.loader.exec_module(content)

    # prep django with the passed in templates
    extra_templates = []
    if 'TEMPLATES' in user_config:
        extra_templates = [settings.TEMPLATES, ]

    boot_django(extra_templates)

    # make the galleries
    make_galleries(content, settings)