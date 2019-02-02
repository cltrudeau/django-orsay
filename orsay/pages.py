import os
from datetime import datetime
from glob import glob

from django.template import loader, Context, Template, TemplateSyntaxError
from django.utils.safestring import mark_safe

from screwdriver import list_to_rows

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
    def __init__(self, dirname, item):
        self.dirname = os.path.abspath(dirname)
        self.caption = ''

        if isinstance(item, tuple) or isinstance(item, list):
            self.partial_name = item[0]
            self.caption = mark_safe(item[1])
        else:
            self.partial_name = item

    def init(self, settings):
        # look for partial_name in the directory
        matches = glob(os.path.join(self.dirname, '*%s*' % self.partial_name))
        if len(matches) > 1:
            print('WARNING!!! Multiple file matches for ', 
                '*%s*, using first' % self.partial_name, matches)

        try:
            self.imagename = matches[0]
        except IndexError:
            raise AttributeError('no match for image *%s*' % self.partial_name)

        thumbname = thumbpath(self.imagename, 'thumb1024w')
        self.thumbname = os.path.relpath(thumbname, settings.ALBUM)
        self.imagename = os.path.relpath(self.imagename, settings.ALBUM)


def slide_set(dirname, *args):
    dirname = os.path.abspath(dirname)
    slides = []
    for item in args:
        slides.append(Slide(dirname, item))

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
        if not self_date:
            return ''

        d = self._date
        return f'{d:%A} {d:%B} {d.day}, {d.year}'


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
