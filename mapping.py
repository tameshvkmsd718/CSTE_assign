import sqlite3

conn = sqlite3.connect('mappings.db')
conn.execute("CREATE TABLE IF NOT EXISTS mappings (sku TEXT PRIMARY KEY, msku TEXT)")
data = [('APL001','MSKU_APPLE'),('BAN002','MSKU_BANANA')]
conn.executemany("INSERT OR IGNORE INTO mappings VALUES (?,?)", data)
conn.commit()
conn.close()
print("Mappings populated")
