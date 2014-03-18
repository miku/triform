#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from triform.task import DefaultTask
import requests
import urllib
import BeautifulSoup
import HTMLParser
import prettytable

class GNDTask(DefaultTask):
    TAG = 'gnd'


class DNBStatus(GNDTask):
    """ List available downloads. """
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


class GNDExtract(GNDTask):
    """ Extract the GND snapshot. """
    pass
