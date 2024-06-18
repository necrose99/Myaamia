#! /usr/bin/python3
import lxml.etree as ET
import sqlite3
# This code is licensed under MIT license (see LICENSE.MD for details)

# Connect to the SQLite database
conn = sqlite3.connect('output.db')
cursor = conn.cursor()

# Create a table to store the XLF data
cursor.execute('''
CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    source TEXT,
    target TEXT
)
''')

# Parse the XLF XML file
tree = ET.parse('input.xlf')
root = tree.getroot()

# Iterate over the XLF elements and insert data into the SQLite table
for element in root.iter('trans-unit'):
    source = element.find('source').text
    target = element.find('target').text
    cursor.execute('INSERT INTO translations (source, target) VALUES (?, ?)', (source, target))

# Commit the changes and close the database connection
conn.commit()
conn.close()
