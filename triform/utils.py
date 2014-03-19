#!/usr/bin/env python
# coding: utf-8

from colorama import Fore, Back, Style
import logging
import os
import random
import re
import string
import subprocess
import tempfile


logger = logging.getLogger('luigi-interface')


def random_string(length=16):
    """ Return a random string (upper and lowercase letters) of length `length`,
    defaults to 16. """
    return ''.join(random.choice(string.letters) for _ in range(length))


def random_tmp_path():
    """ Return a random path, that is located under the system's tmp dir. This
    is just a path, nothing gets touched or created. """
    return os.path.join(tempfile.gettempdir(), 'tasktree-%s' % random_string())


def shellout(template, **kwargs):
    """
    Takes a shell command template and executes it. The template must use
    the new (2.6+) format mini language. `kwargs` must contain any defined
    placeholder, only `output` is optional.
    Raises RuntimeError on nonzero exit codes.

    Simple template:

        wc -l < {input} > {output}

    Quoted curly braces:

        ps ax|awk '{{print $1}}' > {output}

    Usage with luigi:

        ...
        tmp = shellout('wc -l < {input} > {output}', input=self.input().fn)
        luigi.File(tmp).move(self.output.fn())
        ....

    """
    preserve_spaces = kwargs.get('preserve_spaces', False)
    stopover = random_tmp_path()
    if not 'output' in kwargs:
        kwargs.update({'output': stopover})
    ignoremap = kwargs.get('ignoremap', {})
    command = template.format(**kwargs)
    if not preserve_spaces:
        command = re.sub('[ \n]+', ' ', command)
    logger.debug(cyan(command))
    code = subprocess.call([command], shell=True)
    if not code == 0:
        if code in ignoremap:
            logger.info("Ignoring error via ignoremap: %s" % (ignoremap.get(code)))
        else:
            logger.error('%s: %s' % (command, code))
            error = RuntimeError('%s exitcode: %s' % (command, code))
            error.code = code
            raise error
    return kwargs.get('output')


def dim(text):
    return Back.WHITE + Fore.BLACK + text + Fore.RESET + Back.RESET

def green(text):
    return Fore.GREEN + text + Fore.RESET

def red(text):
    return Fore.RED + text + Fore.RESET

def yellow(text):
    return Fore.YELLOW + text + Fore.RESET

def cyan(text):
    return Fore.CYAN + text + Fore.RESET

def magenta(text):
    return Fore.MAGENTA + text + Fore.RESET