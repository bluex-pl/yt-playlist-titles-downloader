ytpd - youtube playlist titles downloader
=========================================

Small script that saves all video titles from YouTube playlist.


* ``python ytpd.py [playlist_URL]``
  will fetch playlist info in a few parts and store video titles in a text file with name dependent on playlist name.

  **example**::

    python ytpd.py http://www.youtube.com/playlist?list=PL75C7F02E0C4EA3E0

* ``python ytpd.py [user_channel_URL]``
  will fetch all public playlists from user.

  **example**::

    python ytpd.py http://www.youtube.com/user/simonscat


Requirements
------------

* Python 3.3
* `Requests <http://python-requests.org/>`_


Credits
-------

ytpd is under development by Szymon Wroblewski <bluex0@gmail.com>