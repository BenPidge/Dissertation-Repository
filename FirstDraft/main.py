from Database import DatabaseSetup, DataExtractor, CoreDatabase


dbSetup = DatabaseSetup.DatabaseSetup()
extractor = DataExtractor.DataExtractor()


def begin():
    """
    Begins the program.
    """
    print("Enter which menu you'd like to use:\n"
          "1. Database Setup\n"
          "2. Data Extractor\n"
          "9. Exit")
    menu = CoreDatabase.int_input("> ")
    if menu == 1:
        dbSetup.begin()
    elif menu == 2:
        extractor.begin()
    else:
        SystemExit(0)
    CoreDatabase.complete_setup()


begin()
