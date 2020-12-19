class Equipment:
    """A class representing a piece of equipment."""

    # a static dictionary that stores all the equipment item names within their appropriate tags.
    tagGroups = {
        "Ammunition": [], "Arcane focus": [], "Artisan's tools": [], "Container": [], "Druidic focus": [],
        "Equipment pack": [], "Finesse": [], "Gaming set": [], "Heavy": [], "Heavy Armor": [],
        "Holy symbol": [], "Light": [], "Light Armor": [], "Loading": [], "Martial Weapon": [], "Medium Armor": [],
        "Musical instrument": [], "Range": [], "Reach": [], "Simple Weapon": [], "Special": [],
        "Stealth Disadvantage": [], "Str Limit": [], "Thrown": [], "Tools": [], "Two-Handed": [], "Versatile": []
    }
    # a static array holding each equipment object, to avoid the need for repeated objects
    allEquipment = []

    def __init__(self, name, tags, description,
                 dice=None, item_range=None, armor_class=0, str_limit=0, weight=0, value="0cp"):
        """
        Stores all the data for a piece of equipment.
        :param name: The name of the equipment.
        :type name: str
        :param tags: Tags applied to help identify the equipment.
        :type tags: list
        :param description: The description explaining the items purpose.
        :type description: str
        :param dice: The dice linked to the item, typically for damage, with the format "(num)d(sides)".
        :type dice: str, optional
        :param item_range: The normal and long range of a weapon, for thrown or ranged attacks.
        :type item_range: list, optional
        :param armor_class: The armor class provided by wearing or wielding the item.
        :type armor_class: int, optional
        :param str_limit: The strength score limit to use the item.
        :type str_limit: int, optional
        :param weight: How much the item weighs, in lb.
        :type weight: int, optional
        :param value: How much the item is worth. Represented using numbers and coin representations cp, sp, gp, pp.
        :type value: str, optional
        """
        if item_range is None:
            item_range = [5, 5]
        self.range = item_range
        self.name = name
        self.tags = tags
        self.description = description
        self.dice = dice
        self.armorClass = armor_class
        self.strLimit = str_limit
        self.weight = weight
        self.value = value

        Equipment.allEquipment.append(self)
        self.sort_to_tags()

    def sort_to_tags(self):
        """Adds a pointer to the object in the tagGroups dictionaries array for each of the objects tags"""
        for tag in self.tags:
            Equipment.tagGroups[tag] = Equipment.tagGroups[tag] + [self.name]


def get_all_equipment():
    """
    Returns the allEquipment class variable
    :return an array of equipment objects
    """
    return Equipment.allEquipment


def get_tag_group(tag):
    """
    Returns a specified tag array from the tagGroups class variable
    :return an array of strings
    """
    return Equipment.tagGroups.get(tag)
