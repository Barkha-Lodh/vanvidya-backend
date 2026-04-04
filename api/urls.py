from django.urls import path
from . import views

urlpatterns = [
    path('external/complete/', views.get_complete_plant_info,
        name='complete_plant_info'),
    path('identify-leaf/', views.identify_plant_from_image,
        name='identify_leaf'),
    path('api/plants/search/advanced/', views.search_plants_by_attributes),
    path('api/plants/category/<str:category>/', views.get_plants_by_category),
]
