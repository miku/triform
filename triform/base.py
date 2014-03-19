#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from triform.format import TSV
from triform.intervals import monthly
from triform.task import DefaultTask
from triform.utils import shellout
import BeautifulSoup
import datetime
import HTMLParser
import logging
import luigi
import prettytable
import re
import requests
import urllib


logger = logging.getLogger('luigi-interface')
today = datetime.date.today


class GNDTask(DefaultTask):
    TAG = 'gnd'

class VIAFTask(DefaultTask):
    TAG = 'viaf'

    def latest(self):
        task = VIAFLatestDate()
        luigi.build([task])
        date, _ = task.output().open().readline().split('\t', 1)
        return date


class DNBStatus(GNDTask):
    """ List available downloads as ASCII table.
        http://i.imgur.com/G4zBWAp.png
    """
    def run(self):
        host = "datendienst.dnb.de"
        path = "/cgi-bin/mabit.pl"
        params = {
            "userID": "opendata",
            "pass": "opendata",
            "cmd": "login",
        }

        r = requests.get('http://{host}{path}?{params}'.format(host=host,
                         path=path, params=urllib.urlencode(params)))
        logger.info(r.url)
        if not r.status_code == 200:
            raise RuntimeError(r)

        soup = BeautifulSoup.BeautifulSoup(r.text)
        tables = soup.findAll('table')
        if not tables:
            raise RuntimeError('No tabular data found on {}'.format(r.url))

        table = tables[0]
        h = HTMLParser.HTMLParser()

        rows = []
        for tr in table.findAll('tr'):
            row = []
            for td in tr.findAll('td'):
                text = ''.join(h.unescape(td.find(text=True)))
                row.append(text)
            rows.append(row)

        x = prettytable.PrettyTable(rows[0])
        for row in rows[1:]:
            x.add_row(row)
        print(x)

    def complete(self):
        return False


class GNDDump(GNDTask):
    """ Download, extract and filter the GND snapshot. """

    date = luigi.DateParameter(default=monthly())

    def run(self):
        host = "datendienst.dnb.de"
        path = "/cgi-bin/mabit.pl"
        params = {
            "userID": "opendata",
            "pass": "opendata",
            "cmd": "fetch",
            "mabheft": "GND.ttl.gz",
        }

        url = 'http://{host}{path}?{params}'.format(host=host,
                                                    path=path,
                                                    params=urllib.urlencode(params))
        output = shellout("""wget --retry-connrefused "{url}" -O {output}""",
                          url=url)
        luigi.File(output).move(self.output().fn)

    def output(self):
        return luigi.LocalTarget(path=self.path(ext='ttl.gz'))


class GNDExtract(GNDTask):
    """ Extract the archive. """

    date = luigi.DateParameter(default=monthly())

    def requires(self):
        return GNDDump(date=self.date)

    def run(self):
        output = shellout("gunzip -c {input} > {output}", input=self.input().fn)
        luigi.File(output).move(self.output().fn)

    def output(self):
        return luigi.LocalTarget(path=self.path(ext='ttl'))


class GNDSameAs(GNDTask):
    """ Convert to N3 via serd, filter stuff we do not need. Takes about 6min. """

    date = luigi.DateParameter(default=monthly())

    def requires(self):
        return GNDExtract(date=self.date)

    def run(self):
        output = shellout("""serdi -b -f -i turtle -o ntriples {input} |
                             grep "owl#sameAs" > {output}""", input=self.input().path)
        luigi.File(output).move(self.output().path)

    def output(self):
        return luigi.LocalTarget(path=self.path(ext='n3'))


class DNBTitleDump(GNDTask):
    pass


class ZDBTitleDump(GNDTask):
    pass


class VIAFDataPage(VIAFTask):
    """ Download Viaf data page.
        Match on http://viaf.org/viaf/data/viaf-20140215-links.txt.gz
    """

    def run(self):
        r = requests.get('http://viaf.org/viaf/data/')
        if not r.status_code == 200:
            raise RuntimeError(r)

        strainer = BeautifulSoup.SoupStrainer('a')
        soup = BeautifulSoup.BeautifulSoup(r.text, parseOnlyThese=strainer)
        with self.output().open('w') as output:
            for link in soup:
                output.write_tsv(link.get('href'))

    def output(self):
        return luigi.LocalTarget(path=self.path(), format=TSV)


class VIAFLatestDate(VIAFTask):
    """" The latest date. """
    date = luigi.DateParameter(default=today())

    def requires(self):
        return VIAFDataPage()

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
        return luigi.LocalTarget(path=self.path(latest=True, ext='nt.gz'), format=TSV)
