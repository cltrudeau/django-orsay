import os

from django.template import loader, Context, Template, TemplateSyntaxError
from screwdriver import list_to_rows, head_tail_middle

from .utils import thumbpath

# ===========================================================================

class Gallery(object):
    def __init__(self, dirname, title, imagename):
        self.dirname = os.path.abspath(dirname)
        self.title = title
        self.image = os.path.abspath(os.path.join(dirname, imagename))

    @classmethod
    def make_filename(cls, num):
        return 'gallery%03d.html' % num

    def init(self, settings, num, is_last):
        # gallery filename settings
        self.num = num
        self.filename = self.make_filename(num)
        self.full_filename = os.path.abspath(os.path.join(settings.ALBUM,
            self.filename))

        self.is_first = num == 1
        self.is_last = is_last

        # gallery thumbnail
        thumbname = thumbpath(self.image, 'thumb500sq')
        self.thumbname = os.path.relpath(thumbname, settings.ALBUM)

    def make_file(self, settings):
        # fetch the template
        template = loader.get_template('gallery.html')

        # get non-hidden files, just the filenames, chop extensions, sort them
        images = []
        with os.scandir(self.dirname) as paths:
            for path in paths:
                if not path.name.startswith('.') and path.is_file():
                    filename = os.path.relpath(path, settings.ALBUM)
                    thumbname = thumbpath(filename, 'thumb150sq')

                    names = (os.path.relpath(filename, settings.ALBUM), 
                        os.path.relpath(thumbname, settings.ALBUM))

                    images.append(names)

        images.sort(key=lambda x: x[0])

        d = {
            'settings':settings,
            'title':self.title,
            'rows':list_to_rows(images, 7),
            'prev':"",
            'next':"",
        }

        if not self.is_first:
            d['prev'] = self.make_filename(self.num - 1)

        if not self.is_last:
            d['next'] = self.make_filename(self.num + 1)

        # render template and write to file
        result = template.render(d)

        with open(self.full_filename, 'w') as f:
            f.write(result)

# ===========================================================================

def make_galleries(content, settings):
    num_galleries = len(content.galleries)
    count = 1

    # create each gallery page
    for gallery in content.galleries:
        gallery.init(settings, count, count == num_galleries)
        gallery.make_file(settings)

        count += 1

    # create the gallery index
    template = loader.get_template('all_galleries.html')

    d = {
        'settings':settings,
        'title':'Galleries',
        'static_path':settings.static_path,
        'rows': list_to_rows(content.galleries, 3)
    }

    # render template and write to file
    result = template.render(d)

    fname = os.path.abspath(os.path.join(settings.ALBUM, 'all_galleries.html'))
    with open(fname, 'w') as f:
        f.write(result)
