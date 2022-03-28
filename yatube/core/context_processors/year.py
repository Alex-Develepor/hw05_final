from django.utils import timezone


def year(request):
    year = timezone.now()
    return {
        'year': year.year
    }
