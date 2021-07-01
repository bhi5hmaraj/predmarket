from sqlalchemy import create_engine 

DATABASE_URI = 'postgres+psycopg2://postgres:^F!zYogjW8aNvNJE2HePXRkr@^woAnaRMqJo7Gdez9#mwCiTWLDkrcff3Vn@localhost:5432/predmarket_dev'

db = create_engine(DATABASE_URI)
db.execute("ALTER TABLE users DROP COLUMN fb_connected;")

result_set = db.execute("SELECT * FROM users")
for row in result_set:
	print(row)

