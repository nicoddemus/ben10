""" test_path.py - Test the path module.

This only runs on Posix and NT right now.  I would like to have more
tests.  You can help!  Just add appropriate pathnames for your
platform (os.name) in each place where the p() function is called.
Then send me the result.  If you can't get the test to run at all on
your platform, there's probably a bug in path.py -- please let me
know!

TempDirTestCase.testTouch() takes a while to run.  It sleeps a few
seconds to allow some time to pass between calls to check the modify
time on files.

URL:     http://www.jorendorff.com/articles/python/path
Author:  Jason Orendorff <jason@jorendorff.com>
Date:    7 Mar 2004

"""
from etk11.filesystem.path import path
import codecs, os, random, shutil, tempfile, time

# This should match the version of path.py being tested.
__version__ = '2.2'


def _p(**choices):
    """ Choose a value from several possible values, based on os.name """
    return choices[os.name]

class Test():
    def testRelpath(self):
        root = path(_p(nt='C:\\',
                      posix='/'))
        foo = root / 'foo'
        quux = foo / 'quux'
        bar = foo / 'bar'
        boz = bar / 'Baz' / 'Boz'
        up = path(os.pardir)

        # basics
        assert root.relpathto(boz) == path('foo') / 'bar' / 'Baz' / 'Boz'
        assert bar.relpathto(boz) == path('Baz') / 'Boz'
        assert quux.relpathto(boz) == up / 'bar' / 'Baz' / 'Boz'
        assert boz.relpathto(quux) == up / up / up / 'quux'
        assert boz.relpathto(bar) == up / up

        # x.relpathto(x) == curdir
        assert root.relpathto(root) == os.curdir
        assert boz.relpathto(boz) == os.curdir
        # Make sure case is properly noted (or ignored)
        assert boz.relpathto(boz.normcase()) == os.curdir

        # relpath()
        cwd = path(os.getcwd())
        assert boz.relpath() == cwd.relpathto(boz)

        if os.name == 'nt':
            # Check relpath across drives.
            d = path('D:\\')
            assert d.relpathto(boz) == boz

    def testStringCompatibility(self):
        """ Test compatibility with ordinary strings. """
        x = path('xyzzy')
        assert x == 'xyzzy'
        assert x == u'xyzzy'

        # sorting
        items = [path('fhj'),
                 path('fgh'),
                 'E',
                 path('d'),
                 'A',
                 path('B'),
                 'c']
        items.sort()
        assert items == ['A', 'B', 'E', 'c', 'd', 'fgh', 'fhj']

        # Test p1/p1.
        p1 = path("foo")
        p2 = path("bar")
        assert p1 / p2 == _p(nt='foo\\bar', posix='foo/bar')

    def testProperties(self):
        # Create sample path object.
        f = _p(nt='C:\\Program Files\\Python\\Lib\\xyzzy.py',
              posix='/usr/local/python/lib/xyzzy.py')
        f = path(f)

        # .parent
        assert f.parent == _p(nt='C:\\Program Files\\Python\\Lib', posix='/usr/local/python/lib')

        # .name
        assert f.name == 'xyzzy.py'
        assert f.parent.name == _p(nt='Lib', posix='lib')

        # .ext
        assert f.ext == '.py'
        assert f.parent.ext == ''

        # .drive
        assert f.drive == _p(nt='C:', posix='')


    def testMethods(self):
        # .abspath()
        assert path(os.curdir).abspath() == os.getcwd()

        # .getcwd()
        cwd = path.getcwd()
        assert isinstance(cwd, path)
        assert cwd == os.getcwd()


    def testUNC(self):
        if hasattr(os.path, 'splitunc'):
            p = path(r'\\python1\share1\dir1\file1.txt')
            assert p.uncshare == r'\\python1\share1'
            assert p.splitunc() == os.path.splitunc(str(p))
