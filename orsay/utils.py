import os

from PIL import Image, ExifTags

from .constants import (THUMB_FILE_EXT, COVER_THUMB_DIR, SLIDE_THUMB_HEIGHT,
    SLIDE_THUMB_WIDTH, COVER_THUMB_SIZE)

# ===========================================================================

def thumbpath(filename, thumbdir):
    """Takes a fully qualified image filename and converts it to its thumbnail 
    equivalent"""

    dirname, relname  = os.path.split(filename)
    base, _ = os.path.splitext(relname)

    thumbname = os.path.join(dirname, thumbdir, base + THUMB_FILE_EXT)
    return thumbname


def rotate_exif(image):
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

    return image


def create_thumbnail(src, dest, thumb_size):
    image = Image.open(src)
    image = rotate_exif(image)

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


def create_cover_image(dirname, src):
    base = os.path.abspath(dirname)
    sq500 = os.path.abspath(os.path.join(base, COVER_THUMB_DIR))
    os.makedirs(sq500, exist_ok=True)

    image_base = os.path.basename(src)
    filename, ext = os.path.splitext(image_base)

    dest = os.path.abspath(os.path.join(sq500, filename + THUMB_FILE_EXT))
    if not os.path.isfile(dest):
        create_thumbnail(src, dest, COVER_THUMB_SIZE)


def create_slide_image(src, dest):
    image = Image.open(src)
    image = rotate_exif(image)

    # want to scale to 1024x768, padding either sides or top if needed
    width, height = image.size

    thumb = Image.new('RGB', (SLIDE_THUMB_WIDTH, SLIDE_THUMB_HEIGHT), (0, 0, 0))

    scale_factor_width = float(width) / float(SLIDE_THUMB_WIDTH)
    scale_factor_height = float(height) / float(SLIDE_THUMB_HEIGHT)

    if scale_factor_width >= scale_factor_height:
        # image isn't same ratio as 1024x768, width scale factor is bigger so
        # use it to scale both dimensions then pad top and bottom
        scaled_width = int(float(width) / scale_factor_width)
        scaled_height = int(float(height) / scale_factor_width)
        scaled = image.resize((scaled_width, scaled_height), Image.LANCZOS)

        thumb.paste(scaled, (0, (SLIDE_THUMB_HEIGHT - scaled_height) // 2))

    elif scale_factor_height > scale_factor_width:
        # height scale factor is bigger, use it to scale both dimensions then
        # pad left and right
        scaled_width = int(float(width) / scale_factor_height)
        scaled_height = int(float(height) / scale_factor_height)
        scaled = image.resize((scaled_width, scaled_height), Image.LANCZOS)

        thumb.paste(scaled, ((SLIDE_THUMB_WIDTH - scaled_width) // 2, 0))

    thumb.save(dest)
