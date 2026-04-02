#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3 as lite
import datetime
import argparse
import os.path
import ntpath
import re
from glob import glob
from xml.etree.ElementTree import tostring, iterparse, ParseError

###################################################################
# TmxSqlite Repository
###################################################################
# Import TMX into a Sqlite database
###################################################################
# Acknowledgements: Gert van Assche's Datamundi TMX to SQL work:
# http://www.datamundi.be/cms/index.php/why-using-sql-on-an-xml-format-like-tmx
###################################################################

def insertTUs(db_con, nodes, count, totalcount):
    cur = db_con.cursor()

    # we make TUs a list of lists of tuples of (segtext, lang) to reduce
    # memory use
    try:
        for e, node in nodes:
            if e == 'end' and node.tag == 'tu':
                segs = []

                orig_tuid = 0
                if 'tuid' in node.attrib: orig_tuid = node.attrib['tuid']

                src = ''
                tgt = ''
                changedate = ''
                changeid = ''
                creationdate = ''
                creationid = ''
                lastusagedate = ''
                usagecount = 0

                for tuv in node.findall('tuv'):
                    lang = tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']

                    if lang == srclang:
                        src = tuv.find('seg').text
                    else:
                        tgtlang = lang
                        tgt = tuv.find('seg').text
                        # changedate = tuv.attrib['changedate'] if 'changedate' in tuv.attrib
                        if 'changedate' in tuv.attrib: changedate = tuv.attrib['changedate']
                        if 'changeid' in tuv.attrib: changeid = tuv.attrib['changeid']
                        if 'creationdate' in tuv.attrib: creationdate = tuv.attrib['creationdate']
                        if 'creationid' in tuv.attrib: creationid = tuv.attrib['creationid']
                        if 'lastusagedate' in tuv.attrib: lastusagedate = tuv.attrib['lastusagedate']
                        if 'usagecount' in tuv.attrib: usagecount = tuv.attrib['usagecount']

                cur.execute("INSERT INTO TranslationUnits VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                    orig_tuid, src, tgt, changedate, changeid, creationdate, creationid, lastusagedate, usagecount,
                    import_id))
                count += 1
                totalcount += 1
                tuid = cur.lastrowid

                sourcefile = None
                for prop in node.iter(tag='prop'):
                    propname = prop.attrib['type']
                    propvalue = prop.text

                    if 'x-ppl:' in propname:
                        cur.execute("INSERT INTO Perplexity VALUES(?, ?, ?)", (tuid, propname, propvalue))
    def insertTUs(db_con, nodes, count, totalcount, import_id):
    cur = db_con.cursor()
    
    # Define the languages we actually care about in our SQL columns
    # This replaces the 'srclang' and 'tgtlang' hardcoding
    target_columns = ['en', 'mia', 'sac', 'mesk', 'pot']

    try:
        for e, node in nodes:
            if e == 'end' and node.tag == 'tu':
                # Initialize a dictionary for this row
                row_data = {lang: None for lang in target_columns}
                orig_tuid = node.attrib.get('tuid', 0)

                # Loop through EVERY translation variant in the TU
                for tuv in node.findall('tuv'):
                    # Get the lang (e.g., 'mia' or 'en-US')
                    full_lang = tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                    
                    # Normalize lang codes (e.g., 'en-US' -> 'en')
                    lang_key = full_lang.split('-')[0].lower()
                    
                    seg_node = tuv.find('seg')
                    if seg_node is not None and seg_node.text:
                        if lang_key in row_data:
                            row_data[lang_key] = seg_node.text

                # Build the dynamic SQL Insert
                # This ensures your Sauk (sac) and Myaamia (mia) end up in the same record
                cur.execute("""
                    INSERT INTO TranslationUnits (orig_tuid, en_text, mia_text, sac_text, mesk_text, pot_text, import_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (orig_tuid, row_data['en'], row_data['mia'], row_data['sac'], row_data['mesk'], row_data['pot'], import_id))
                
                count += 1
                totalcount += 1
                node.clear()
    except Exception as e:
        print(f"Error: {e}")
        db_con.commit()
    
    return count, totalcount

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('--dbname', action='store_true', help='Specify Database name - default is ./tmxdb1.db.')
    #parser.add_argument('--company', action='store_true', help='Specify company name or owner of TM.')
    #parser.add_argument('--domain', action='store_true', help='Specify domain of import - if known.')
    parser.add_argument('--dropTables', action='store_true', help='Drop tables - don''t merge.')
    parser.add_argument(dest='infiles', nargs='+', help='list of tmx files to be imported')
    args = parser.parse_args()

    start = str(datetime.datetime.now())
    print >> sys.stderr, '\nPython TmRepository: Tmx2Sqlite Import'
    print >> sys.stderr, '   Import Started:\t' + start
    #sys.exit()

    totalcount = 0

    con = None
    # To do: pull from argument list
    con = lite.connect('tmxdb.sqlite')
    cur = con.cursor()

    if args.dropTables:
        cur.execute("DROP TABLE IF EXISTS TmxImportFiles")
        cur.execute("DROP TABLE IF EXISTS TranslationUnits")
        cur.execute("DROP TABLE IF EXISTS TranslationUnit")
        cur.execute("DROP TABLE IF EXISTS Properties")
        cur.execute("DROP TABLE IF EXISTS Perplexity")

    cur.execute("CREATE TABLE IF NOT EXISTS TmxImportFiles(id INTEGER PRIMARY KEY AUTOINCREMENT, company, domain, sourcelang, targetlang, tmxfile, started, completed)")
    cur.execute("CREATE TABLE IF NOT EXISTS TranslationUnits(id INTEGER PRIMARY KEY AUTOINCREMENT, orig_tuid INT, Source, Target, changedate, changeid, creationdate, creationid, lastusagedate, usagecount INT, import_id INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS Properties(tuid INT, PropertyName, PropertyValue)")
    cur.execute("CREATE TABLE IF NOT EXISTS Perplexity(tuid INT, domain, perplexity REAL)")

    # make list of infiles that works in both windows & linux
    infiles = []
    for x in args.infiles:
        infiles += glob(x)

    while infiles:
        tmx_file = infiles.pop()

        count = 0

        print >> sys.stderr, '\n\tImporting TMX File into SQLite3: ' + tmx_file
        print >> sys.stderr, '\tStarted:\t' + str(datetime.datetime.now())

        # use iterparse to process large tmx files, instead of in-memory.
        nodes = iter(iterparse(tmx_file, ['start', 'end']))
        _, root = next(nodes)
        _, header = next(nodes)

        # Assuming only one target language
        srclang = header.attrib['srclang']
        # Will get get the target language at the end
        tgtlang = ''

        # Insert header record into database
        started = str(datetime.datetime.now())
        cur.execute("INSERT INTO TmxImportFiles(sourcelang, tmxfile, started) VALUES(?, ?, ?)", (srclang, tmx_file, started))
        import_id = cur.lastrowid

        # loop to take care of TUs
        count, totalcount = insertTUs(con, nodes, count, totalcount)

        completed = str(datetime.datetime.now())
        print >> sys.stderr, '\tCompleted:\t' + completed
        cur.execute("UPDATE TmxImportFiles SET targetlang = ?, completed = ? WHERE id = ?", (tgtlang, completed, import_id))

        print >> sys.stderr, '\t' + str(count) + ' records inserted'

    con.commit()
    con.close()

    print >> sys.stderr, '\nPython TmRepository: Tmx2Sqlite Import Completed!'
    print >> sys.stderr, '   Import Started:   ' + start
    print >> sys.stderr, '   Import Completed: ' + str(datetime.datetime.now())
    print >> sys.stderr, '   Total Records Inserted:\t' + str(totalcount)
