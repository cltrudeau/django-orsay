import os, inspect
from datetime import datetime

from django.template import loader
from django.utils.safestring import mark_safe

from screwdriver import list_to_rows

from .constants import SLIDE_THUMB_DIR, COVER_THUMB_DIR
from .utils import thumbpath

# ===========================================================================

class Section(object):
    def init(self, settings):
        pass


class TextSection(Section):
    template = 'text_section.html'

    def __init__(self, text):
        self.text = mark_safe(text)


class Title(Section):
    template = 'title_section.html'

    def __init__(self, text, hr=True):
        self.text = mark_safe(text)
        self.hr = hr


class Slide(Section):
    def __init__(self, dirname, item, error_trace):
        self.dirname = os.path.abspath(dirname)
        self.thumbdir = os.path.abspath(os.path.join(dirname, SLIDE_THUMB_DIR))
        self.error_trace = error_trace
        self.caption = ''

        if isinstance(item, tuple) or isinstance(item, list):
            self.name_ends_in = str(item[0])
            self.caption = mark_safe(' '.join(item[1:]))
        else:
            self.name_ends_in = str(item)

    def init(self, settings):
        # look for files that end with name_ends_in in the directory
        matches = []
        for filename in os.listdir(self.dirname):
            filename = os.path.abspath(os.path.join(self.dirname, filename))
            if os.path.isfile(filename):
                filename_only = os.path.basename(filename)
                name, ext = os.path.splitext(filename_only)
                if name.lower().endswith(self.name_ends_in.lower()):
                    matches.append(filename)

        if len(matches) > 1:
            print('WARNING!!! Multiple file matches for ', 
                '*%s*, using first' % self.name_ends_in, matches)

        try:
            self.imagename = matches[0]

            if not os.path.isfile(self.imagename):
                raise AttributeError(
                    'matched image for %s was not a file: %s' % (
                        self.name_ends_in, self.imagename))
        except IndexError:
            msg = 'no match for image *%s*; error likely near %s' % (
                self.name_ends_in, self.error_trace)
            raise AttributeError(msg)

        thumbname = thumbpath(self.imagename, SLIDE_THUMB_DIR)
        self.thumbname = os.path.relpath(thumbname, settings.ALBUM)
        self.imagename = os.path.relpath(self.imagename, settings.ALBUM)


def slide_set(dirname, *args):
    # store calling location so that if we error out when generating the
    # thumbnails we can inform the user where it happened
    stack = inspect.stack()
    calling_frame = stack[1]
    error = 'line %s of %s' % (calling_frame.lineno, calling_frame.filename)

    dirname = os.path.abspath(dirname)
    slides = []
    for item in args:
        slides.append(Slide(dirname, item, error))

    return slides


carousel_count = 1

class Carousel(Section):
    template = 'carousel_section.html'

    def __init__(self, *args):
        global carousel_count

        self.slides = []
        self.carousel_id = 'carousel%d' % carousel_count
        carousel_count += 1
        for slide_sets in args:
            self.slides.extend(slide_sets)

    def init(self, settings):
        for slide in self.slides:
            slide.init(settings)


class Page(object):
    def __init__(self, filename, title, date, cover_image, *args):
        self.filename = filename
        self.title = title
        self.cover_image = os.path.abspath(cover_image)
        
        self._date = ''
        if date:
            self._date = datetime.strptime(date, '%Y-%m-%d').date()

        self.sections = []

        for section in args:
            if isinstance(section, str):
                self.sections.append(TextSection(section))
            else:
                self.sections.append(section)

    @property
    def date(self):
        if not self._date:
            return ''

        d = self._date
        return f'{d:%A} {d:%B} {d.day}, {d.year}'

    @property
    def cover_image_thumbnail(self):
        return thumbpath(self.cover_image, COVER_THUMB_DIR)

    def init(self, settings, prev_page, next_page):
        self.prev_page = prev_page
        self.next_page = next_page
        self.cover_image = os.path.relpath(os.path.join(settings.ALBUM,
            self.cover_image))
        self.full_filename = os.path.abspath(os.path.join(settings.ALBUM,
            self.filename))

        for section in self.sections:
            section.init(settings)

    def make_file(self, settings):
        # fetch the template
        template = loader.get_template('page.html')

        d = {
            'settings':settings,
            'page':self,
        }

        # render template and write to file
        result = template.render(d)

        with open(self.full_filename, 'w') as f:
            f.write(result)

# ===========================================================================

def make_pages(content, settings):
    print('Generating trip pages')
    output_filenames = set([])
    for i in range(0, len(content.pages)):
        page = content.pages[i]
        if i == len(content.pages) - 1:
            next_page = None
        else:
            next_page = content.pages[i+1].filename

        if i == 0:
            prev_page = None
        else:
            prev_page = content.pages[i-1].filename

        page.init(settings, prev_page, next_page)
        if page.filename in output_filenames:
            raise AttributeError(
                'Multiple pages configured named %s' % page.filename)

        output_filenames.add(page.filename)

    for page in content.pages:
        page.make_file(settings)

    # create the index page
    template = loader.get_template('all_pages.html')

    d = {
        'settings':settings,
        'title':settings.ALBUM_TITLE,
        'static_path':settings.static_path,
        'rows': list_to_rows(content.pages, 2)
    }

    # render template and write to file
    result = template.render(d)

    fname = os.path.abspath(os.path.join(settings.ALBUM, 'index.html'))
    with open(fname, 'w') as f:
        f.write(result)
