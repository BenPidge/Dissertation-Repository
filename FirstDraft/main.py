from Database import DatabaseSetup

db = DatabaseSetup.DatabaseSetup()
db.setup_tables()
db.print_all_added_data()
db.add_item()
db.complete_setup()
