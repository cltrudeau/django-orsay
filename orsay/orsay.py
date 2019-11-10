import glob, os, shutil, subprocess

from PIL import Image, ExifTags

from screwdriver import DictObject

from .boot_django import boot_django
from .gallery import make_galleries
from .pages import make_pages

# ===========================================================================

def make_album(content, user_config):
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

# ---------------------------------------------------------------------------

def _thumbnail(src, dest, thumb_size):
    image = Image.open(src)

    # handle exif orientation
    #   -- lots of magic numbers in this code, found it at:
    #        https://stackoverflow.com/questions/13872331
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = dict(image._getexif().items())
        
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # ignore image without exif info
        pass

    # create a padded square before shrinking
    width, height = image.size
    if width > height:
        square = Image.new('RGBA', (width, width), (255, 0, 0, 0))
        square.paste(image, (0, (width - height) // 2))
    elif height > width:
        square = Image.new('RGBA', (height, height), (255, 0, 0, 0))
        square.paste(image, ((height - width) // 2, 0))
    else:
        square = image

    # shrink it
    thumb = square.resize((thumb_size, thumb_size), Image.LANCZOS)
    thumb.save(dest)


def make_gallery_thumbnails(dirlist):
    """Uses the Pillow image library to create the 150x150 thumbnails for the 
    gallery pages.

    :param dirlist: list of strings of directories to run the generation on
    """

    extensions = ['jpg', 'gif']

    for dirname in dirlist:
        print('Generating thumbnails for %s' % dirname)

        base = os.path.abspath(dirname)
        sq150 = os.path.abspath(os.path.join(base, 'thumb150sq'))
        os.makedirs(sq150, exist_ok=True)
        
        pictures = []
        for ext in extensions:
            pictures.extend(glob.glob(base + '/*.' + ext))
            pictures.extend(glob.glob(base + '/*.' + ext.upper()))

        print('   ', end='')
        for src in pictures:
            base = os.path.basename(src)
            filename, ext = os.path.splitext(base)

            dest = os.path.abspath(os.path.join(sq150, filename + '.png'))
            if not os.path.isfile(dest):
                _thumbnail(src, dest, 150)

            print('.', end='', flush=True)

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
        base = os.path.abspath(gallery.dirname)
        sq500 = os.path.abspath(os.path.join(base, 'thumb500sq'))
        os.makedirs(sq500, exist_ok=True)

        image_base = os.path.basename(gallery.image)
        filename, ext = os.path.splitext(image_base)

        dest = os.path.abspath(os.path.join(sq500, filename + '.png'))
        if not os.path.isfile(dest):
            _thumbnail(gallery.image, dest, 500)

        print('.', end='', flush=True)

    print()
