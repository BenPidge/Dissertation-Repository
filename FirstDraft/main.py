from Database import DatabaseSetup

db = DatabaseSetup.DatabaseSetup()
db.setup_tables()
db.print_added_data()
# db.removeItem("Spell", "6")
db.add_item()
db.complete_setup()
