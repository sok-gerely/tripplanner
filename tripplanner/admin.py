from django.contrib import admin


from .models import Station,Line,StationOrder,Service,TimetableData,Delay

class StationOrderInline(admin.TabularInline):
    model=StationOrder
    fk_name="line"

class ServiceInline(admin.TabularInline):
    model=Service

class TimetableDataInline(admin.TabularInline):
    model=TimetableData
    fk_name="service"

class DelayInline(admin.TabularInline):
    model=Delay

class LineAdmin(admin.ModelAdmin):
    inlines=[
        ServiceInline,
        StationOrderInline,
        ]

class ServiceAdmin(admin.ModelAdmin):
    inlines=[
        TimetableDataInline,
        ]

class TimetableDataAdmin(admin.ModelAdmin):
    inlines=[
        DelayInline,
    ]

admin.site.register(Station)
admin.site.register(Line,LineAdmin)
admin.site.register(StationOrder)
admin.site.register(Service,ServiceAdmin)
admin.site.register(TimetableData,TimetableDataAdmin)
admin.site.register(Delay)