Basics
======

This whole thing is a quick hack. You create a couple of scripts that use
Orsay objects and it generates a static album for you based on its templates.

You typically want to create:

* content.py
* make_albums.py
* make_thumbnails.py

Content is broken down into pages and galleries. Typically pages are used for
a narrative while galleries are just a large display of pictures.

Sample content.py:

.. code-block:: python

    from importlib import import_module

    from orsay.gallery import Gallery
    from orsay.pages import Page, Title, Carousel, slide_set

    # ===========================================================================

    galleries = [
        Gallery('../00_StMartin', 'St Martin', 'DSC_2642.JPG'), 
    ]

    pages = [
        Page('stamartin.html', 'St Martin', '2023-01-29', 
            '../00_StMartin/DSC_2642.JPG',

            Title('St Martin Sunday Jan 29 - Feb 6, 2023', hr=False),

            Carousel(
                slide_set('../00_StMartin', 
                    'DSC_2638', 'DSC_2639', 'DSC_2641', 'DSC_2642', 'DSC_2643',
                )
            ),
        ),
    ]

Page objects can take any number of ``Title``, strings,  or ``Carousel``
objects. ``Title`` objects are section headers, strings are paragraph text.
Carousel objects take any number of objects returned from the ``slide_set``
factory.  The ``slide_set`` factory takes the name of a directory and any
number of file names (without extensions, partial match on names allowed, for
example can just use the integer portion of an image file name), or a tuple
containing a filename part and a caption.

Sample make_albums.py:

.. code-block:: python

    #!/usr/bin/env python

    import os

    from orsay.orsay import make_album
    import content

    # ===========================================================================

    CURR_DIR = os.path.abspath(os.path.dirname(__file__))
    PARENT = os.path.dirname(CURR_DIR)
     
    config = dict(
        ALBUM_TITLE='St Martin 2023',
        CONTENT=os.path.abspath(os.path.join(CURR_DIR, 'content.py')),
        STATIC=os.path.abspath(os.path.join(CURR_DIR, 'static')),
        ALBUM=os.path.abspath(os.path.join(PARENT, 'album')),
        CSS='style.css',
    )

    make_album(content, config)

For more info on ``make_thumbnails.py`` see the thumbnails.rst file.
