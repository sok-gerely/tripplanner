from django.contrib import admin


from .models import Station,Line,StationOrder,Service,TimetableData

admin.site.register(Station)
admin.site.register(Line)
admin.site.register(StationOrder)
admin.site.register(Service)
admin.site.register(TimetableData)