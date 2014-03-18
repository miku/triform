#!/usr/bin/env python
# coding: utf-8

"""
Default task
============

A default task, that covers file system layout.

"""

from luigi.task import flatten
import hashlib
import json
import logging
import luigi
import os
import re
import slugify

HOME = '/tmp/triform'

logger = logging.getLogger('luigi-interface')


def convert(name):
    """ Convert CamelCase to underscore,
    http://stackoverflow.com/a/1176023/89391. """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def unwrap(s, cut=None):
    """ Remove newlines and repeated spaces from a string. """
    if not isinstance(s, basestring):
        return s
    s = re.sub(r'\s+', ' ', s.strip().replace('\n', ''))
    if not cut is None:
        return s[:cut] + '...'
    return s


class DefaultTask(luigi.Task):
    """
    A default class for finc. Expects a TAG (SOURCE_ID) on the class,
    that gets turned into a instance attribute by the
    `luigi.Task` __metaclass__.
    """
    TAG = NotImplemented

    def parameter_set(self):
        """ Return the parameters names as set. """
        params = set()
        for k, v in self.__class__.__dict__.iteritems():
            if isinstance(v, luigi.Parameter):
                params.add(k)
        return params

    def fingerprint(self, default='output', latest=False, ignore=None, hash=False):
        """
        The fingerprint of a task is a string consisting of the names
        and values of the parametes. `latest` is a special thing, if it is
        `True` then call the `latest()` function on self for the `date` value
        instead of the given date.
        """
        if ignore is None:
            ignore = set()
        parts = set()
        for p in self.parameter_set():
            if p in ignore:
                continue
            if p in ('date', 'end') and latest is True:
                if hasattr(self, 'latest') and hasattr(self.latest, '__call__'):
                    parts.add('latest-%s' % slugify.slugify(str(self.latest())))
                else:
                    # TODO: latest should be allowed to be both a function and
                    # an attribute
                    raise RuntimeError('latest need to be a callable for now')
            else:
                parts.add('%s-%s' % (p, slugify.slugify(str(getattr(self, p)))))
        fingerprint = '-'.join(sorted(parts))
        if len(fingerprint) == 0:
            fingerprint = default
        if hash:
            return hashlib.sha1(fingerprint).hexdigest()
        return fingerprint

    def path(self, filename=None, ext='tsv', latest=False, ignore=None):
        """
        Autogenerate a path based on some category (those are only
        conventions), the tag (source id) and the name of the class and a given
        extension.

        If `latest` is set to true, use `self.latest` value as value for `date`.+

        Ignore takes an iterable with parameters to ignore.
        """
        if self.TAG == NotImplemented:
            raise ValueError('Class or superclass must set TAG (e.g. source id).')

        klassname = convert(self.__class__.__name__)

        if filename is None:
            filename = '%s.%s' % (self.fingerprint(latest=latest, ignore=ignore), ext)
        return os.path.join(HOME, str(self.TAG), klassname, filename)

    def asset(self, path):
        """ Return the absolute path to the asset. `path is the relative path
        below the assets root dir. """
        return os.path.join(os.path.dirname(__file__), 'assets', path)

    def shell(self):
        """ Drop into a shell for debugging. """
        from IPython.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed(banner1="Inside %s" % self.__class__.__name__)
        ipshell()

    def run(self):
        """ About this source/namespace. """
        directory = os.path.abspath(os.path.join(os.path.dirname(self.path()), '..'))
        about = '#TODO: Placeholder'
        try:
            about = unwrap(self.__doc__.strip())
        except AttributeError as err:
            pass
        subclasses = dict([(c.__name__, unwrap(c.__doc__, cut=80))
                           for c in self.__class__.__subclasses__()])
        print(json.dumps({
            'name': self.__class__.__name__.lower().replace('task', ''),
            'about': about,
            'subclasses': subclasses,
            'tag': self.TAG,
            'dir': directory,
        }, indent=4))

