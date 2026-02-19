from .external_apis import PlantDataAggregator, HindiTranslator


def populate_plant_from_api(plant_name):
    """
    Helper function to get complete plant data from all APIs
    Usage: data = populate_plant_from_api('Rose')
    """
    aggregator = PlantDataAggregator()
    return aggregator.get_complete_plant_data(plant_name)


def translate_to_hindi(text):
    """
    Helper function to translate English to Hindi
    Usage: result = translate_to_hindi('Rose')
    """
    translator = HindiTranslator()
    return translator.translate_to_hindi(text)


def translate_to_english(text):
    """
    Helper function to translate Hindi to English
    Usage: result = translate_to_english('गुलाब')
    """
    translator = HindiTranslator()
    return translator.translate_to_english(text)