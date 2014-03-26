# coding: utf-8

"""
GND-related tasks.
"""

from gluish.intervals import monthly
from gluish.shell import shellout
from gluish.task import BaseTask
import BeautifulSoup
import HTMLParser
import luigi
import prettytable
import requests
import urllib


class GNDTask(BaseTask):
    TAG = 'gnd'


class DNBStatus(GNDTask):
    """ List available downloads. For human eyes only. """
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
    """ Download the GND snapshot. """

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
