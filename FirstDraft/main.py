from Database import DatabaseSetup, DataExtractor, CoreDatabase, DataConverter, CharacterBuilder
from Optimisation import Chromosome
from Visuals import VisualsController


visuals = VisualsController.VisualsController()


def testing():
    character = DataConverter.create_character(1)
    chromosome = Chromosome.Chromosome(character, [["Dexterous", 0.4], ["Heavy Weapons", 0.6], ["Ranged", 0.4]], 0.5, 0.5)
    print(chromosome)


def begin():
    """
    Begins the program.
    """
    print("Enter which service you'd like to use:\n"
          "1. Visuals\n"
          "2. Database Setup\n"
          "3. Data Extractor\n"
          "4. Data Converter\n"
          "5. View Tables\n"
          "6. Character Builder\n"
          "7. General testing\n"
          "9. Exit")
    menu = CoreDatabase.int_input("> ")
    DataConverter.create_all_equipment()
    if menu == 1:
        visuals.begin()
    elif menu == 2:
        DatabaseSetup.begin()
    elif menu == 3:
        DataExtractor.begin()
    elif menu == 4:
        DataConverter.begin()
    elif menu == 5:
        CoreDatabase.view_tables()
    elif menu == 6:
        CharacterBuilder.begin()
    elif menu == 7:
        testing()
    else:
        SystemExit(0)
    CoreDatabase.complete_setup()


begin()
