from django.contrib import admin


from .models import Station,Line,StationOrder,Service,Timetable,TimetableData,Delay

admin.site.register(Station)
admin.site.register(Line)
admin.site.register(StationOrder)
admin.site.register(Service)
admin.site.register(Timetable))
admin.site.register(TimetableData)
admin.site.register(Delay)