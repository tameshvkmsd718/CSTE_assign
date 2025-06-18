from flask import Flask, request, render_template
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SKUMapper:
    def __init__(self, db_path='mappings.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS mappings (
                sku TEXT PRIMARY KEY,
                msku TEXT
            )
        """)
        self.conn.commit()

    def map_sku(self, sku):
        if not sku or pd.isna(sku): return 'UNMAPPED'
        sku_u = sku.strip().upper()
        row = self.conn.execute("SELECT msku FROM mappings WHERE sku = ?", (sku_u,)).fetchone()
        return row[0] if row else 'UNMAPPED'

@app.route('/', methods=['GET','POST'])
def upload_file():
    tables = None
    msg = ''
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            msg = 'No file uploaded'
        else:
            fp = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(fp)
            ext = os.path.splitext(fp)[1].lower()
            try:
                df = pd.read_excel(fp) if ext in ['.xlsx','.xls'] else pd.read_csv(fp, encoding='utf-8', errors='ignore')
            except Exception as e:
                msg = f'Error reading file: {e}'
            else:
                if 'SKU' not in df:
                    msg = "Error: 'SKU' column is required."
                else:
                    mapper = SKUMapper()
                    df['MSKU'] = df['SKU'].apply(mapper.map_sku)
                    tables = df.head(20).to_html(index=False)
    return render_template('index.html', tables=tables, msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
