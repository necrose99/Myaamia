#! /usr/bin/python3
import sqlite3
import os
import subprocess

# (c) 2011 Necrose99 ,Miami Nation ,   Others 
# This code is licensed under MIT license (see LICENSE.MD for details)
# https://github.com/necrose99/Myaamia
# 
# Souces,   https://mc.miamioh.edu/ilda-myaamia/dictionary/ , Miami Nation of 'Indy , OK, others.. 
## chatgpt for RAD/prototyping code 
## create wordlist one can strip it.. namily of English 
## myself being dyslexic/adhd doing as system compiles to lean mia....  ensure dictonary in MIA is cleaned .. 
## iso/mia/Myaamia
## bake a spell checking Dictonary from word/s list if more words are added sort them if in Mysql db / Sort by alphabetic order 
## give an sql file 
## consume dictionary-src.txt  add to db , sort  output new dictionary.txt all nice and sorted /ignore duplicates
#
## for Microsoft Word dictionary.txt cp/copy to Myaamia.dic and enjoy.. 
## Aspell-Hunspell , Libree Office .dictionary.txt cp/copy to  Firefox-ext MIA_US-Myaamia.dic 
### Aspell-Hunspell (MIA_US-Myaamia.aff ruleset linguistic ruleset needs further refinment)  likely feedback from linguists / ai to assit in inputing rulsets 
### Google Chrome wants MIA_US-Myaamia.aff MIA_US-Myaamia.dic can use them raw.. 
### then a glossary/dictonary  file for TMX ie Weblate  , dictonary for spell checking or ai translation..
### Potawatami , Lakota or other languages have parralles 

def read_dictionary_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        dictionary_entries = [line.strip() for line in file.readlines()]
    return dictionary_entries

def save_dictionary_to_file(dictionary_entries, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in dictionary_entries:
            file.write(f"{entry}\n")

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dictionary (
        word TEXT PRIMARY KEY
    )
    ''')
    conn.commit()
    return conn

def insert_entries_to_database(entries, conn):
    cursor = conn.cursor()
    for entry in entries:
        try:
            cursor.execute("INSERT INTO dictionary (word) VALUES (?)", (entry,))
        except sqlite3.IntegrityError:
            # Entry already exists, ignore duplicates
            pass
    conn.commit()

def fetch_all_entries_from_database(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary")
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def export_sql_dump(db_path, sql_dump_path):
    try:
        # Use subprocess to call the sqlite3 command line tool
        subprocess.run(['sqlite3', db_path, '.dump'], stdout=open(sql_dump_path, 'w'), check=True)
    except Exception as e:
        print(f"An error occurred while exporting SQL dump: {e}")

def main():
    input_file = 'dictionary.txt'
    db_file = 'dictionary.db'
    output_file = 'exported_dictionary.txt'
    sql_dump_file = 'dictionary.sql'

    # Step 1: Read dictionary from file
    dictionary_entries = read_dictionary_from_file(input_file)

    # Step 2: Sort entries alphabetically
    dictionary_entries.sort()

    # Step 3: Initialize the database
    conn = initialize_database(db_file)

    # Step 4: Insert entries into the database
    insert_entries_to_database(dictionary_entries, conn)

    # Step 5: Fetch all unique entries from the database
    all_entries = fetch_all_entries_from_database(conn)

    # Step 6: Sort the fetched entries alphabetically
    all_entries.sort()

    # Step 7: Save the updated dictionary back to a new text file
    save_dictionary_to_file(all_entries, output_file)

    # Step 8: Export the database schema and data to an SQL file
    export_sql_dump(db_file, sql_dump_file)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()