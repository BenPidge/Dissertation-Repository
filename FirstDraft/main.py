from Database import DatabaseSetup, DataExtractor, CoreDatabase, DataConverter
from Visuals import SelectorMenu


selectorMenu = SelectorMenu.SelectorMenu()


def begin():
    """
    Begins the program.
    """
    print("Enter which service you'd like to use:\n"
          "1. Selector Menu\n"
          "2. Database Setup\n"
          "3. Data Extractor\n"
          "4. Data Converter\n"
          "5. View Tables\n"
          "9. Exit")
    menu = CoreDatabase.int_input("> ")
    DataConverter.create_all_equipment()
    if menu == 1:
        selectorMenu.begin()
    elif menu == 2:
        DatabaseSetup.begin()
    elif menu == 3:
        DataExtractor.begin()
    elif menu == 4:
        DataConverter.begin()
    elif menu == 5:
        CoreDatabase.view_tables()
    else:
        SystemExit(0)
    CoreDatabase.complete_setup()


begin()
