from django.contrib import admin
from .models import Station,Line,StationOrder,Service,TimetableData,Delay
from django.forms.models import ModelForm
from django.contrib.auth.models import Group,User
from merged_inlines.admin import MergedInlineAdmin

admin.site.unregister(Group)
admin.site.unregister(User)

class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will get validated and saved."""
        return True

class StationOrderInline(admin.TabularInline):
    model = StationOrder
    fk_name = "line"
    extra = 0
    exclude = ('station_to',)

class LastStationOrderInline(admin.TabularInline):
    model = StationOrder
    fk_name = "line"
    extra = 0
    fields = ('station_to',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        line_id = qs.values_list('line')[0][0]
        line = Line.objects.get(pk=line_id)
        last_station = line.get_last_station()
        return qs.filter(station_to=last_station)

class ServiceInline(admin.TabularInline):
    model=Service
    extra=0
    show_change_link=True
    form = AlwaysChangedModelForm

class DelayInline(admin.TabularInline):
    model=Delay
    extra=0

class TimetableDataInline(admin.TabularInline):
    model=TimetableData
    fk_name="service"
    readonly_fields=('station',)
    fields=('station','date_time',)
    extra = 0
    max_num = model.station_num
    can_delete = False
    show_change_link=True

"""class MergedStationOrderInlines(MergedInlineAdmin):
    inlines = [StationOrderInline, LastStationOrderInline,]"""

class LineAdmin(admin.ModelAdmin):
    inlines=[
        ServiceInline,
        StationOrderInline,
        LastStationOrderInline,
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
admin.site.register(Service,ServiceAdmin)
admin.site.register(TimetableData,TimetableDataAdmin)