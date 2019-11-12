Thumbnails for "orsay"
======================

Prior to version 0.3.0 you had to generate your own thumbnails with something
like ImageMagick. This is now done with Pillow. Two calls have been added for
generating gallery thumbnails: "make_gallery_thumbnails()" and
"make_gallery_covers". 

A quick script to generate your thumbnail images that takes a list of
directory names to generate them for:

.. code-block:: python

    import sys

    from orsay.orsay import make_gallery_covers, make_gallery_thumbnails
    import content

    # =========================================================================

    make_gallery_thumbnails(sys.argv[1:])
    make_gallery_covers(content)  


Where you have defined a file called "content.py" which contains the list of 
gallery objects.

The "make_album()" call now generates whatever thumbnails it needs for the
slideshows that you define. 

Details
=======

Three types of thumbnails are needed for the various pages created with orsay.
Each directory where your images are found will have the necessary thumbnail
directories created:

* thumb150sq
* thumb500sq
* thumb1024w

The first two are used for thumbnails for the galleries pages and the index
pages. These create square images padded with transparency, 150x150 and
500x500 respectively.

The third is used for the carousels. These slide carousels currently use
1024x768. Thumbs retain their aspect ratio and are padded with black
backgrounds.

All thubmnails are be created in .png format in order to support
transparency. 

ImageMagick
===========

Equivalent ImageMagick methods for generating the thumbnails are:

Square Thumbnails
-----------------

.. code-block:: bash

    $ cd album-directory
    $ mkdir thumb500sq
    $ mogrify -auto-orient -path thumb500sq -format gif -thumbnail '500x500>' -gravity center -extent 500x500 -background transparent '*.JPG'


Carousel Thumbnails
-------------------

.. code-block:: bash

    $ cd album-directory
    $ mkdir thumb1024w
    $ mogrify -auto-orient -path thumb1024w -format gif -thumbnail '1024x768>' -gravity center -extent 1024x768 -background black '*.JPG'

