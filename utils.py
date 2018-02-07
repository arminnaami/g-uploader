# -*- coding: utf-8 -*-
'''
The Utils class contains many functions for project-wide use.
'''

import os
import sys
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import random
import logging
import re
from concurrent import futures  # if python2, a backport is needed
from math import log
import shutil


def combine_files(parts, dest):
    '''
    Combines files.

    :param parts: Source files.
    :type parts: list of strings
    :param dest: Destination file.
    :type dest: string

    '''
    chunkSize = 1024 * 1024 * 4

    if len(parts) == 1:
        shutil.move(parts[0], dest)
    else:
        with open(dest, 'wb') as output:
            for part in parts:
                with open(part, 'rb') as input:
                    data = input.read(chunkSize)
                    while data:
                        output.write(data)
                        data = input.read(chunkSize)
                os.remove(part)


def url_fix(s, charset='utf-8'):
    '''
    Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    >>> url_fix('http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param s: Url address.
    :type s: string
    :param charset: The target charset for the URL if the url was
                    given as unicode string. Default is 'utf-8'.
    :type charset: string
    :rtype: string

    (taken from `werkzeug.utils <http://werkzeug.pocoo.org/docs/utils/>`_)
    '''
    if sys.version_info < (3, 0) and isinstance(s, str):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urllib.parse.urlsplit(s)
    path = urllib.parse.quote(path, '/%')
    qs = urllib.parse.quote_plus(qs, ':&=')
    return urllib.parse.urlunsplit((scheme, netloc, path, qs, anchor))


def progress_bar(progress, length=20):
    '''
    Returns a textual progress bar.

    >>> progress_bar(0.6)
    '[##########--------]'

    :param progress: Number between 0 and 1 describes the progress.
    :type progress: float
    :param length: The length of the progress bar in chars. Default is 20.
    :type length: int
    :rtype: string
    '''
    length -= 2  # The brackets are 2 chars long.
    if progress < 0:
        progress = 0
    if progress > 1:
        progress = 1
    return "[" + "#" * int(progress * length) + "-" * (length - int(progress * length)) + "]"


def is_HTTPRange_supported(url, timeout=15):
    '''
    Checks if a server allows `Byte serving <https://en.wikipedia.org/wiki/Byte_serving>`_,
    using the Range HTTP request header and the Accept-Ranges and Content-Range HTTP response headers.

    :param url: Url address.
    :type url: string
    :param timeout: Timeout in seconds. Default is 15.
    :type timeout: int
    :rtype: bool
    '''
    url = url.replace(' ', '%20')

    fullsize = get_filesize(url)
    if not fullsize:
        return False

    headers = {'Range': 'bytes=0-3'}
    req = urllib.request.Request(url, headers=headers)
    urlObj = urllib.request.urlopen(req, timeout=timeout)
    filesize = int(urlObj.headers["Content-Length"])

    urlObj.close()
    return (filesize != fullsize)


def get_filesize(url, timeout=15):
    '''
    Fetches file's size of a file over HTTP.

    :param url: Url address.
    :type url: string
    :param timeout: Timeout in seconds. Default is 15.
    :type timeout: int
    :returns: Size in bytes.
    :rtype: int
    '''
    # url = url_fix(url)
    try:
        urlObj = urllib.request.urlopen(url, timeout=timeout)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return 0
    try:
        file_size = int(urlObj.headers["Content-Length"])
    except (IndexError, KeyError, TypeError):
        return 0

    return file_size


def get_random_useragent():
    '''
    Returns a random popular user-agent.
    Taken from `here <http://techblog.willshouse.com/2012/01/03/most-common-user-agents/>`_, last updated on 04/01/2017.

    :returns: user-agent
    :rtype: string
    '''
    l = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    ]
    return random.choice(l)


def sizeof_human(num):
    '''
    Human-readable formatting for filesizes. Taken from `here <http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size>`_.

    >>> sizeof_human(175799789)
    '167.7 MB'

    :param num: Size in bytes.
    :type num: int

    :rtype: string
    '''
    unit_list = list(zip(['B', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2]))

    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024 ** exponent
        unit, num_decimals = unit_list[exponent]

        if sys.version_info >= (2, 7):  # python2.7 supports comma seperators
            format_string = '{:,.%sf} {}' % (num_decimals)
            return format_string.format(quotient, unit)
        else:  # with python2.6, we have to do some ugly hacks
            if quotient != int(quotient):  # real float
                x, y = str(quotient).split('.')
                x = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1,", "%d" % int(x))
                y = y[:num_decimals]
                quotient = "%s.%s" % (x, y) if y else x
                return "%s %s" % (quotient, unit)
            else:
                quotient = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1,", "%d" % quotient)
                return "%s %s" % (quotient, unit)

    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def time_human(duration, fmt_short=False):
    '''
    Human-readable formatting for timing. Based on code from `here <http://stackoverflow.com/questions/6574329/how-can-i-produce-a-human-readable-difference-when-subtracting-two-unix-timestam>`_.

    >>> time_human(175799789)
    '6 years, 2 weeks, 4 days, 17 hours, 16 minutes, 29 seconds'
    >>> time_human(589, fmt_short=True)
    '9m49s'

    :param duration: Duration in seconds.
    :type duration: int
    :param fmt_short: Format as a short string (`47s` instead of `47 seconds`)
    :type fmt_short: bool
    :rtype: string
    '''
    duration = int(duration)
    if duration == 0:
        return "0s" if fmt_short else "0 seconds"

    INTERVALS = [1, 60, 3600, 86400, 604800, 2419200, 29030400]
    if fmt_short:
        NAMES = ['s' * 2, 'm' * 2, 'h' * 2, 'd' * 2, 'w' * 2, 'y' * 2]
    else:
        NAMES = [('second', 'seconds'),
                 ('minute', 'minutes'),
                 ('hour', 'hours'),
                 ('day', 'days'),
                 ('week', 'weeks'),
                 ('month', 'months'),
                 ('year', 'years')]

    result = []

    for i in range(len(NAMES) - 1, -1, -1):
        a = duration // INTERVALS[i]
        if a > 0:
            result.append((a, NAMES[i][1 % a]))
            duration -= a * INTERVALS[i]

    if fmt_short:
        return "".join(["%s%s" % x for x in result])
    return ", ".join(["%s %s" % x for x in result])


def create_debugging_logger():
    '''
    Creates a debugging logger that prints to console.

    :rtype: `logging.Logger` instance
    '''
    t_log = logging.getLogger('pySmartDL')
    t_log.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # console.setFormatter(logging.Formatter('[%(levelname)s@%(thread)d] %(message)s'))
    console.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    t_log.addHandler(console)
    return t_log


class DummyLogger(object):
    '''
    A dummy logger. You can call `debug()`, `warning()`, etc on this object, and nothing will happen.
    '''

    def __init__(self):
        pass

    def dummy_func(self, *args, **kargs):
        pass

    def __getattr__(self, name):
        if name.startswith('__'):
            return object.__getattr__(name)
        return self.dummy_func


class ManagedThreadPoolExecutor(futures.ThreadPoolExecutor):
    '''
	Managed Thread Pool Executor. A subclass of ThreadPoolExecutor.
    '''

    def __init__(self, max_workers):
        futures.ThreadPoolExecutor.__init__(self, max_workers)
        self._futures = []

    def submit(self, fn, *args, **kwargs):
        future = super(ManagedThreadPoolExecutor, self).submit(fn, *args, **kwargs)
        self._futures.append(future)
        return future

    def done(self):
        return all([x.done() for x in self._futures])

    def get_exceptions(self):
        l = []
        for x in self._futures:
            if x.exception():
                l.append(x.exception())
        return l

