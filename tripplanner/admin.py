from django.contrib import admin


from .models import Station,Line,StationOrder,Service,TimetableData,Delay

class StationOrderInline(admin.TabularInline):
    model=StationOrder
    fk_name="line"
    extra=0

class ServiceInline(admin.TabularInline):
    model=Service
    extra=0

class TimetableDataInline(admin.TabularInline):
    model=TimetableData
    fk_name="service"
    readonly_fields=('station',)
    fields=('station','date_time',)
    extra = 0
    can_delete = False

class DelayInline(admin.TabularInline):
    model=Delay
    extra=0

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
    readonly_fields=('station',)

admin.site.register(Station)
admin.site.register(Line,LineAdmin)
admin.site.register(StationOrder)
admin.site.register(Service,ServiceAdmin)
admin.site.register(TimetableData,TimetableDataAdmin)
admin.site.register(Delay)