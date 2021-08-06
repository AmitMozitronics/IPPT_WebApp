from django.contrib.gis.geoip2 import GeoIP2

def show_user_time(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    g = GeoIP2()
    ip_details = g.city(ip)
    user_time_zone = ip_details['time_zone']
    return user_time_zone