from .models import Genre

def genres_processor(request):
    return {
        'genres': Genre.objects.all()
    }