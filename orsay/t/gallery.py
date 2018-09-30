#!/usr/bin/env python

import os

from django.template import loader, Context, Template, TemplateSyntaxError

from orsay.boot_django import boot_django
from screwdriver import list_to_rows, head_tail_middle

# ===========================================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALBUM_DIR = os.path.abspath(os.path.join(BASE_DIR, '../album'))
PAGES_DIR = os.path.abspath(os.path.join(ALBUM_DIR, 'pages'))
STATIC_DIR = os.path.abspath(os.path.join(ALBUM_DIR, 'static'))

TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, 'templates'))

PHOTO_DIRS = [
#    ('zzz_Test', 'zzz Test'),
    ('000_Sept11', 'Tuesday September 11', 'DSC_0061.JPG'), 
    ('000_Sept12', 'Wednesday September 12','DSC_0250.JPG'),
    ('000_Sept13', 'Thursday September 13', 'DSE00705.JPG'),
    ('000_Sept14', 'Friday September 14', 'DSC_0522.JPG'),
    ('000_Sept15','Saturday September 15', 'DSC_0815.JPG'),
    ('000_Sept16', 'Sunday September 16', 'DSD_0061.JPG'),
    ('000_Sept17', 'Monday September 17', 'DSD_0474.JPG'),
    ('000_Sept18','Tuesday September 18', 'DSE00905.JPG'),
]

boot_django([TEMPLATE_DIR, ])

# ===========================================================================

def get_thumbname(thumbdir, image):
    thumbname = thumbdir + '/' + os.path.splitext(image)[0] + '.gif'
    return thumbname


def gallery_page(dirname, title, num, is_first, is_last):
    # fetch the template
    template = loader.get_template('gallery.html')

    # get non-hidden files, just the filenames, chop extensions, sort them
    images = []
    with os.scandir(dirname) as paths:
        for path in paths:
            if not path.name.startswith('.') and path.is_file():
                relname = os.path.split(path)[1]
                images.append( (relname, get_thumbname('thumb150sq', relname)) )

    images.sort(key=lambda x: x[0])

    d = {
        'title':title,
        'dirname':os.path.relpath(dirname, PAGES_DIR),
        'static_path':os.path.relpath(STATIC_DIR, PAGES_DIR) + '/',
        'prev':"",
        'next':"",
    }

    if not is_first:
        d['prev'] = 'gallery%03d.html' % (num - 1)

    if not is_last:
        d['next'] = 'gallery%03d.html' % (num + 1)

    d['rows'] = list_to_rows(images, 7)

    # render template and write to file
    result = template.render(d)

    fname = os.path.abspath(os.path.join(PAGES_DIR, 'gallery%03d.html' % num))
    with open(fname, 'w') as f:
        f.write(result)


def gallery_index():
    template = loader.get_template('all_galleries.html')

    d = {
        'title':'Galleries',
        'static_path':os.path.relpath(STATIC_DIR, PAGES_DIR) + '/',
    }

    specs = []
    count = 1
    for item in PHOTO_DIRS:
        # name, image, gallery
        name = item[1]
        dirname = os.path.abspath(os.path.join(BASE_DIR, '..', item[0]))
        thumbname = get_thumbname('thumb500sq', item[2])
        image = os.path.join(dirname, thumbname)
        image = os.path.relpath(image, PAGES_DIR)
        gallery = os.path.join(PAGES_DIR, 'gallery%03d.html' % count)
        gallery = os.path.relpath(gallery, PAGES_DIR)

        specs.append( (name, image, gallery) )
        count += 1

    d['rows'] = list_to_rows(specs, 3)
    # render template and write to file
    result = template.render(d)

    fname = os.path.abspath(os.path.join(PAGES_DIR, 'all_galleries.html'))
    with open(fname, 'w') as f:
        f.write(result)


# ===========================================================================
# Main
# ===========================================================================


def make_gallery(spec, num, first, last):
    dirname = os.path.abspath(os.path.join(BASE_DIR, '..', spec[0]))
    gallery_page(dirname, spec[1], count, first, last)


# create the gallery pages

count = 1
head, middle, tail = head_tail_middle(PHOTO_DIRS)
make_gallery(head, count, True, tail == None)
count += 1
for g in middle:
    make_gallery(g, count, False, False)
    count += 1

if tail:
    make_gallery(tail, count, False, True)


# create the gallery listing
gallery_index()
