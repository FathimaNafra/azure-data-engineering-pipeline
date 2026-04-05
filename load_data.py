import pandas as pd
import pyodbc

# 🔹 Load your CSV (change path) - skip completely bad rows
df = pd.read_csv(r"C:\Users\iyehi\OneDrive\Desktop\cleaned_netflix.csv", on_bad_lines='skip')

# 🔹 Keep only named columns (drop empty Unnamed columns)
df = df.iloc[:, :13]

# 🔹 Replace NaN with None (important for SQL)
df = df.where(pd.notnull(df), None)

# 🔹 Convert numeric columns to avoid type errors
df['show_id'] = pd.to_numeric(df['show_id'], errors='coerce').fillna(0).astype(int)
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').fillna(0).astype(int)
df['year_added'] = pd.to_numeric(df['year_added'], errors='coerce').fillna(0).astype(int)

# 🔹 Connect to Azure SQL
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=azuresqlserver1212.database.windows.net;'
        'DATABASE=processed_dataset_db;'
        'UID=CloudSAd904fa8f;'
        'PWD=Nafranafhan@2001;'  # Try without URL encoding first
        'Encrypt=yes;TrustServerCertificate=no;'
    )
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

cursor = conn.cursor()
inserted = 0
failed = 0

# 🔹 Insert data row by row with error handling
for _, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO cleaned_netflix (show_id, title, director, cast, country, date_added, release_year, rating, duration, listed_in, description, type, year_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
        inserted += 1
        
        # Commit every 100 rows for safety
        if inserted % 100 == 0:
            conn.commit()
            print(f"✓ Inserted {inserted} rows...")
    except Exception as e:
        failed += 1
        if failed <= 5:  # Print first 5 errors
            print(f"✗ Error on row: {e}")

# Final commit for remaining rows
conn.commit()
conn.close()

print(f"✅ DONE! Inserted {inserted} rows, {failed} rows failed")