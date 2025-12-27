from django.core.management import call_command
from django.http import HttpResponse

def load_restaurants(request):
    if request.user.is_superuser:
        try:
            call_command('loaddata', 'restaurants.json')
            return HttpResponse('Restaurants loaded successfully!')
        except Exception as e:
            return HttpResponse(f'Error: {e}')
    return HttpResponse('Unauthorized', status=401)
