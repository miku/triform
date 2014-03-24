# coding: utf-8

"""
VIAF-related tasks.
"""

from gluish.shell import shellout
from gluish.task import BaseTask
from gluish.format import TSV
import BeautifulSoup
import datetime
import luigi
import re
import requests

today = datetime.date.today


class VIAFTask(BaseTask):
    TAG = 'viaf'

    def closest(self):
        task = VIAFLatestDate()
        luigi.build([task])
        date, _ = task.output().open().readline().split('\t', 1)
        return date


class VIAFDataURLList(VIAFTask):
    """ Download Viaf data page.
        Match on http://viaf.org/viaf/data/viaf-20140215-links.txt.gz
    """
    date = luigi.DateParameter(default=today())
    url = luigi.Parameter(default='http://viaf.org/viaf/data/')

    def run(self):
        r = requests.get(self.url)
        if not r.status_code == 200:
            raise RuntimeError(r)

        strainer = BeautifulSoup.SoupStrainer('a')
        soup = BeautifulSoup.BeautifulSoup(r.text, parseOnlyThese=strainer)
        with self.output().open('w') as output:
            for link in soup:
                output.write_tsv(link.get('href'))

    def output(self):
        return luigi.LocalTarget(path=self.path(digest=True), format=TSV)


class VIAFLatestDate(VIAFTask):
    """" The latest date. """
    date = luigi.DateParameter(default=today())

    def requires(self):
        return VIAFDataURLList()

    def run(self):
        with self.input().open() as handle:
            for row in handle:
                pattern = "http://viaf.org/viaf/data/viaf-(\d{8})-clusters-rdf.nt.gz"
                mo = re.match(pattern, row)
                if mo:
                    date = datetime.datetime.strptime(mo.group(1), '%Y%m%d').date()
                    with self.output().open('w') as output:
                        output.write_tsv(date, mo.group())
                    break
            else:
                raise RuntimeError('Could not find latest date.')

    def output(self):
        return luigi.LocalTarget(path=self.path(), format=TSV)


class VIAFDump(VIAFTask):
    """ Download the latest dump. Dynamic, uses the link from VIAFLatestDate. """

    date = luigi.DateParameter(default=today())

    def requires(self):
        return VIAFLatestDate()

    def run(self):
        with self.input().open() as handle:
            _, url = handle.readline().strip().split('\t', 1)
            output = shellout("""wget --retry-connrefused "{url}" -O {output}""",
                              url=url)
            luigi.File(output).move(self.output().fn)

    def output(self):
        cbmap = {'date': lambda obj: obj.closest()}
        return luigi.LocalTarget(path=self.path(cbmap=cbmap, ext='nt.gz'),
                                 format=TSV)

