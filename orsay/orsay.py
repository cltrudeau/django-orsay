import glob, os, shutil, subprocess

from PIL import Image, ExifTags

from screwdriver import DictObject

from .constants import (GALLERY_THUMB_DIR, THUMB_FILE_EXT, GALLERY_THUMB_SIZE,
    COVER_THUMB_DIR)
from .boot_django import boot_django
from .gallery import make_galleries
from .pages import make_pages, Carousel
from .utils import (create_thumbnail, create_cover_image, create_slide_image)

# ===========================================================================

def make_album(content, user_config):
    print('Generating album')
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

    # prep django with the passed in templates
    extra_templates = []
    if 'TEMPLATES' in user_config:
        extra_templates = [settings.TEMPLATES, ]

    boot_django(extra_templates)

    # make the content
    make_galleries(content, settings)
    make_pages(content, settings)
    make_trip_images(content)

# ---------------------------------------------------------------------------

def make_gallery_thumbnails(dirlist):
    """Uses the Pillow image library to create the 150x150 thumbnails for the 
    gallery pages.

    :param dirlist: list of strings of directories to run the generation on
    """

    extensions = ['jpg', 'gif']

    for dirname in dirlist:
        print('Generating thumbnails for %s' % dirname)

        base = os.path.abspath(dirname)
        sq150 = os.path.abspath(os.path.join(base, GALLERY_THUMB_DIR))
        os.makedirs(sq150, exist_ok=True)
        
        pictures = []
        for ext in extensions:
            pictures.extend(glob.glob(base + '/*.' + ext))
            pictures.extend(glob.glob(base + '/*.' + ext.upper()))

        first = True
        for src in pictures:
            base = os.path.basename(src)
            filename, ext = os.path.splitext(base)

            dest = os.path.abspath(os.path.join(sq150, filename +
                THUMB_FILE_EXT))
            if not os.path.isfile(dest):
                if first:
                    print('   ', end='')
                    first = False

                print('.', end='', flush=True)
                create_thumbnail(src, dest, GALLERY_THUMB_SIZE)

        if not first:
            print()


def make_gallery_covers(content):
    """Uses the Pillow image library to create 500x500 thumbnails for the
    cover shots for each gallery index. Uses "content.py" to find what images
    to create.

    :param content: content object
    """
    print('Generating covers for gallery index page')
    print('   ', end='')

    for gallery in content.galleries:
        create_cover_image(gallery.dirname, gallery.image)
        print('.', end='', flush=True)

    print()


def make_trip_images(content):
    """Uses the Pillow image library to generate thumbnails for the trip index
    pages and the the 1024 wide images used in the carousels. 

    :param content: content object with pages list in it
    """
    print('Generating carousel images')

    first = True
    for page in content.pages:
        cover_image = os.path.abspath(page.cover_image)
        dirname = os.path.dirname(cover_image)
        create_cover_image(dirname, cover_image)

        for section in page.sections:
            if not isinstance(section, Carousel):
                # only looking for carousels
                continue

            # --- section is a carousel
            for slide in section.slides:
                # make sure there is a directory for the image
                os.makedirs(slide.thumbdir, exist_ok=True)

                # create image
                src = os.path.abspath(slide.imagename)
                dest = os.path.abspath(slide.thumbname)

                if not os.path.isfile(dest):
                    if first:
                        first = False
                        print('   ', end='')

                    print('.', end='', flush=True)
                    create_slide_image(src, dest)

    if not first:
        print()
