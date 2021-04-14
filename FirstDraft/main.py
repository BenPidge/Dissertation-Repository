from Database import DatabaseSetup, DataExtractor, CoreDatabase, DataConverter, CharacterBuilder
from Optimisation import Chromosome, ChromosomeController
from Visuals import VisualsController


visuals = VisualsController.VisualsController()


def testing():
    ChromosomeController.begin()


def begin():
    """
    Begins the program.
    """
    DataConverter.create_all_equipment()
    visuals.begin()
    # CoreDatabase.complete_setup()


begin()
