from Database import CharacterBuilder, DataConverter, CoreDatabase as Db
from Optimisation.Chromosome import Chromosome
from pymoo.algorithms.nsga2 import NSGA2


currentGen = []
nondominatedFront = []


def build_chromosome(filters):
    """
    Builds a chromosome and adds it to the list of current chromosomes.
    :param filters: the filters to use to build the chromosome
    :type filters: dict
    """
    # retrieves the needed filters for building a chr
    convertedFilters = []
    for heading, elements in filters.items():
        choiceType = heading[:-1]
        whereFrom = ["Background", "ClassOptions", "RaceOptions"]
        if heading in ("Proficiencies", "Skills"):
            choiceType = "Proficiency"
        elif heading == "Spells":
            whereFrom = ["Race", "Class"]
        elif heading == "Equipment":
            choiceType = "Equipment"
            whereFrom = ["Class"]
        elif heading in ("Background", "Class", "Race"):
            choiceType = heading
            whereFrom = [heading]
            elements = [elements]
        elif heading in ("Subrace", "Subclass"):
            choiceType = heading
            whereFrom = [heading.replace("Sub", "").capitalize()]
            elements = [elements]
        elif heading != "Languages":
            choiceType = ""

        if choiceType != "":
            for element in elements:
                convertedFilters.append([element, choiceType, whereFrom])

    # builds a character
    convertedFilters = CharacterBuilder.take_choices(convertedFilters)
    newChr = DataConverter.create_character(1, convertedFilters, filters["Abilities"])

    # extracts the tags for the selected archetypes
    primaryArch = filters["Primary"]
    try:
        secondaryArch = filters["Secondary"]
    except KeyError:
        secondaryArch = None
    healthWeight, magicWeight, tags = extract_tags(primaryArch, secondaryArch)

    # combines it all to make a chromosome
    tags = [[i, j] for (i, j) in tags.items()]
    currentGen.append(Chromosome(newChr, tags, magicWeight, healthWeight))
    print(currentGen[0])


def extract_tags(primary_arch, secondary_arch=None):
    """
    Extracts the tags and their calculated weighting from archetypes.
    :param primary_arch: the name of the primary archetype
    :type primary_arch: str
    :param secondary_arch: the name of the secondary archetype
    :type secondary_arch: str
    :return: The health weighting, the magic weighting, and a dictionary linking tags to their weights
    """
    archWeights = (2, 1)
    tags = dict()
    healthWeight = 0
    magicWeight = 0
    if secondary_arch is None:
        secondary_arch = primary_arch

    archCount = 0
    for arch in [primary_arch, secondary_arch]:
        Db.cursor.execute(f"SELECT archetypeId, healthWeighting, magicWeighting FROM Archetype "
                          f"WHERE archetypeName='{arch}'")

        for (archId, healthWeighting, magicWeighting) in Db.cursor.fetchall():
            healthWeight += healthWeighting * archWeights[archCount]
            magicWeight += magicWeighting * archWeights[archCount]

            Db.cursor.execute(f"SELECT tagName, tagId FROM Tag WHERE tagId IN ("
                              f"SELECT tagId FROM ArchetypeTag WHERE archetypeId={str(archId)})")
            for (name, tagId) in Db.cursor.fetchall():
                Db.cursor.execute(f"SELECT weighting FROM ArchetypeTag WHERE tagId={str(tagId)}")
                if name in tags.keys():
                    newVal = tags[name] + float(Db.cursor.fetchone()[0]) * archWeights[archCount]
                else:
                    newVal = float(Db.cursor.fetchone()[0]) * archWeights[archCount]
                tags.update({name: round(newVal, 2)})

        archCount += 1
    return round(healthWeight, 2), round(magicWeight, 2), tags


def begin_optimising():
    # look at Pymoo notes for explanations during implementation
    # this is all currently a reference for the layout

    # problem = get_problem(x)
    # algorithm = NSGA2(pop_size=100, ...)
    # ?
    # nondominatedFront = problem.pareto_front()
    return None

