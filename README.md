README
======

Objective. Given a GND or multiple GNDs, return a set of interesting attributes
for the GND in question. GNDs can be people, corporate bodies, geographic locations.

The GND ontology is a [DNB standard](http://d-nb.info/standards/elementset/gnd).

What class can a GND be?

 * Administrative unit
 * Authority Resource
 * Building or memorial
 * Characters or morphemes
 * Collection
 * Collective manuscript
 * Collective pseudonym
 * Conference or Event
 * Corporate Body
 * Country
 * Differentiated person
 * Earlier name of the person
 * Ethnographic name
 * Extraterrestrial territory
 * Family
 * Fictive corporate body
 * Fictive place
 * Fictive term
 * Fuller form of the name of the person
 * Gods
 * Group of persons
 * Historic single event or era
 * Language
 * Later name of the person
 * Literary or legendary character
 * Manuscript
 * Means of transport with individual name
 * Member state
 * Musical work
 * Name of small geographic unit lying within another geographic unit
 * Name of the person
 * Natural geographic unit
 * Nomenclature in biology or chemistry
 * Organ of corporate body
 * Person
 * Place or geographic name
 * Preferred name of the person
 * Product name or brand name
 * Project or program
 * Provenance characteristic
 * Pseudonym
 * Pseudonym name of the person
 * Real name of the person
 * Religious territory
 * Royal or member of a royal house
 * Series of conference or event
 * Software product
 * Spirits
 * Subject heading
 * Subject heading senso stricto
 * Territorial corporate body or administrative unit
 * Undifferentiated person
 * Variant name of the person
 * Version of a musical work,
 * Way, border or line
 * Work

What is the distribution of these classes?

    $ time egrep -o  "a gndo:[a-zA-Z0-9_-]+" GND.ttl | awk '{print $2}' | sort | uniq -c


Problems with GND virtuoso
--------------------------

    GND.ttl.gz from 2014/03/12

    OpenLink Interactive SQL (Virtuoso), version 0.9849b.
    Type HELP; for help and EXIT; to exit.
    SQL> DB.DBA.TTLP_MT(file_to_string_output('/Users/tir/tmp/GND.ttl'),
                        '', 'http://gndapps.com', 160);
    Connected to OpenLink Virtuoso
    Driver: 07.10.3207 OpenLink Virtuoso ODBC Driver

    *** Error 42000: [Virtuoso Driver][Virtuoso Server]RDFGE: rdf box with a geometry
          rdf type and a non geometry content
    at line 1 of Top-Level:
    DB.DBA.TTLP_MT(file_to_string_output('/Users/tir/tmp/GND.ttl'),
                   '', 'http://gndapps.com', 160)

Does this work?

    DB.DBA.RDF_LOAD_RDFXML_MT(file_to_string_output('/Users/tir/tmp/GND.rdf'),
                              '', 'http://gndapps.com', 224);

Prototype
---------

Build a mapping table, that has the following columns:

    gnd | url to dbpedia rdf | url to viaf rdf | date_added | date_updated

* For each GND, follow the `sameAs` property to find dbpedia equivalents.
* For each DBPedia page, find `sameAs` backlinks to GND or VIAF.


Build a depication cache:

    gnd | depiction url | date_added | date_updated


External Services
-----------------

* http://sameas.org, has dbpedia links, gnd and viaf and a couple more ...
* sent an email to contact@sameas.org about data freshness (17/3/2014)


Prior art
---------

Indexing Linked Bibliographic Data with JSON-LD, BibJSON and Elasticsearch

* http://journal.code4lib.org/articles/7949

> This paper presents a novel solution for representing and indexing
  bibliographic resources that retains the data integrity and extensibility of
  Linked Data while supporting fast, customizable indexes in an application-
  friendly data format.

> Combining multiple heterogeneous data sources for use in the same application
  typically requires considerable work on data transformation.

> How can we bring data from distributed sources together onto a single search
  platform?

Here, BibJSON, JSON-LD and elasticsearch.


JSON-LD (and GND)
-----------------

* http://api.lobid.org/context/gnd.json


How could a first iteration look?
---------------------------------

Compontents:

* A simple *sameAs service* that updates itself continuously.

A spider, that given a single GND:

* checks the type of the GND (person, place, etc.)
* retrieves all related documents (via sameAs service)
* will filter out a number of predicates, that has been configured for a certain
  resource type (e.g. birthdays for people, capital for countries, etc.)
* maybe, rank the properties by source
* filter out properties that have the same predicate and object
  (only keep the highest ranked source)
* construct a JSON-LD probably, with all information condensed into a single file
* deliver the JSON
* format the JSON via some frontend library, or do some serverside rendering (HTML)

