Thumbnails for "orsay" with Image Magick
========================================

Three types of thumbnails are needed for the various pages created with orsay.
For each image directory you have you need to create three thumbnail
directories:

* thumb150sq
* thumb500sq
* thumb1024w

The first two are used for thumbnails for the galleries pages and the index
pages. The third is used for the carousels. They need to be generated
differently.

All thubmnails will be created in .gif format in order to support
transparency. Remember that different cameras use different extension names
and you may need to generate for both '\*.JPG', '\*.jpg' and possible '\*.gif'

Square Thumbnails
-----------------

Generate the square thumbnails with transparent backgrounds:

.. code-block:: bash

    $ cd album-directory
    $ mkdir thumb500sq
    $ mogrify -auto-orient -path thumb500sq -format gif -thumbnail '500x500>' -gravity center -extent 500x500 -background transparent '*.JPG'


Carousel Thumbnails
-------------------

Thumbnails for the carousel are padded differently and use a black background

.. code-block:: bash

    $ cd album-directory
    $ mkdir thumb1024w
    $ mogrify -auto-orient -path thumb1024w -format gif -thumbnail '1024x768>' -gravity center -extent 1024x768 -background black '*.JPG'

