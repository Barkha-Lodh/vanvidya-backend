from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.external_apis import (
    WikipediaAPI, GeminiPlantAPI, GroqPlantAPI, GoogleTranslateAPI)


@api_view(['GET'])
def get_complete_plant_info(request):
    plant_name = request.GET.get('name', '')
    if not plant_name:
        return Response({'error': 'Plant name required'},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        # Wikipedia
        wiki_desc, wiki_img, wiki_url = WikipediaAPI.get_plant_info(plant_name)

        # Try Groq first (more reliable for now)
        api_data = GroqPlantAPI.get_plant_data(plant_name)
        if not api_data:
            api_data = GeminiPlantAPI.get_plant_data(plant_name)




        # Gemini (preferred) or Groq (backup)
        #api_data = GeminiPlantAPI.get_plant_data(plant_name)
        #if not api_data:
          #  api_data = GroqPlantAPI.get_plant_data(plant_name)
        # Hindi name
        hindi_name = GoogleTranslateAPI.translate_to_hindi(plant_name)
        if api_data and api_data.get('hindi_name'):
            hindi_name = api_data['hindi_name']
        result = {
            'common_name': plant_name,
            'hindi_name': hindi_name,
            'description': wiki_desc or 'Not available',
            'image_url': wiki_img,
            'wikipedia_url': wiki_url,
            'scientific_name': api_data.get('scientific_name','') if api_data else '',
            'family': api_data.get('family','') if api_data else '',
            'watering': api_data.get('watering','') if api_data else '',
            'sunlight': api_data.get('sunlight','') if api_data else '',
            'soil_type': api_data.get('soil_type','') if api_data else '',
            'indoor_outdoor': api_data.get('indoor_outdoor','') if api_data else '',
            'edible': api_data.get('edible','') if api_data else '',
            'toxic': api_data.get('toxic','') if api_data else '',
            'warning': api_data.get('warning') if api_data else None,
            'fun_facts': api_data.get('fun_facts','') if api_data else '',
            'origin': api_data.get('origin','') if api_data else '',
            'growth_rate': api_data.get('growth_rate','') if api_data else '',
            'diseases': api_data.get('diseases',[]) if api_data else []
        }
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def identify_plant_from_image(request):
    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'error': 'No image provided'},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        # Gemini Vision identifies plant
        gemini_vision = GeminiPlantAPI.identify_from_image(image_file)
        if not gemini_vision:
            return Response({'error': 'Identification failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        plant_name = gemini_vision.get('plant_name', 'Unknown')
        if plant_name == 'Unknown':
            return Response({'error': 'Could not identify'},
                status=status.HTTP_404_NOT_FOUND)
        # Get full details
        api_data = GeminiPlantAPI.get_plant_data(plant_name)
        wiki_desc, wiki_img, wiki_url = WikipediaAPI.get_plant_info(plant_name)
        hindi_name = GoogleTranslateAPI.translate_to_hindi(plant_name)
        if api_data and api_data.get('hindi_name'):
            hindi_name = api_data['hindi_name']
        response_data = {
            'plant_identification': {
                'plant_name': plant_name,
                'confidence': gemini_vision.get('confidence', 0),
                'identified_by': 'Gemini 2.0 Flash Vision'
            },
            'disease_detection': {
                'is_healthy': gemini_vision.get('is_healthy', True),
                'disease': gemini_vision.get('disease')
            },
            'plant_details': {
                'common_name': plant_name,
                'hindi_name': hindi_name,
                'scientific_name': gemini_vision.get('scientific_name') or
                    (api_data.get('scientific_name','') if api_data else ''),
                'family': api_data.get('family','') if api_data else '',
                'description': wiki_desc or 'Not available',
                'image_url': wiki_img,
                'wikipedia_url': wiki_url,
                'watering': api_data.get('watering','') if api_data else '',
                'sunlight': api_data.get('sunlight','') if api_data else '',
                'soil_type': api_data.get('soil_type','') if api_data else '',
                'indoor_outdoor': api_data.get('indoor_outdoor','') if api_data else '',
                'edible': api_data.get('edible','') if api_data else '',
                'toxic': api_data.get('toxic','') if api_data else '',
                'warning': api_data.get('warning') if api_data else None,
                'fun_facts': api_data.get('fun_facts','') if api_data else '',
                'origin': api_data.get('origin','') if api_data else '',
                'growth_rate': api_data.get('growth_rate','') if api_data else '',
                'diseases': api_data.get('diseases',[]) if api_data else []
            }
        }
        return Response(response_data)
    except Exception as e:
        return Response({'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
