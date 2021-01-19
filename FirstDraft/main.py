from Database import DatabaseSetup, DataExtractor, CoreDatabase, DataConverter


dbSetup = DatabaseSetup.DatabaseSetup()


def begin():
    """
    Begins the program.
    """
    print("Enter which service you'd like to use:\n"
          "1. Database Setup\n"
          "2. Data Extractor\n"
          "3. Data Converter\n"
          "4. View Tables\n"
          "9. Exit")
    menu = CoreDatabase.int_input("> ")
    if menu == 1:
        dbSetup.begin()
    elif menu == 2:
        DataExtractor.begin()
    elif menu == 3:
        DataConverter.begin()
    elif menu == 4:
        CoreDatabase.view_tables()
    else:
        SystemExit(0)
    CoreDatabase.complete_setup()


begin()
