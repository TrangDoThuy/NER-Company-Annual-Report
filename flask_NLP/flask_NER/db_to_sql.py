import sqlite3

conn = sqlite3.connect('annual_reports.db')

with open('db_slqlite.sql', "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        # f.write('%s\n' % line)
        f.write(f'{line}\n')

conn.close()