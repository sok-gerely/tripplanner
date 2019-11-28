from django.contrib import admin
from .models import Station,Line,StationOrder,Service,TimetableData,Delay
from django.forms.models import ModelForm
from django.contrib.auth.models import Group,User

admin.site.unregister(Group)
admin.site.unregister(User)

class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will get validated and saved."""
        return True

class StationOrderInline(admin.TabularInline):
    model=StationOrder
    fk_name="line"
    extra=0

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


class LineAdmin(admin.ModelAdmin):
    inlines=[
        ServiceInline,
        StationOrderInline,
        ]
    list_display = ('name','type',)
    list_filter = ('type',)

class ServiceAdmin(admin.ModelAdmin):
    inlines=[
        TimetableDataInline,
        ]
    list_display = ('line','departure_time','type','valid_from','valid_until','fee')
    list_filter = ('line','type','valid_from','valid_until',)

class TimetableDataAdmin(admin.ModelAdmin):
    inlines=[
        DelayInline,
    ]
    readonly_fields=('station',)
    list_display = ('service','station','date_time',)
    list_filter = ('service','station',)
    def has_add_permission(self, request, obj=None):
        return False

class StationAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Station,StationAdmin)
admin.site.register(Line,LineAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(TimetableData,TimetableDataAdmin)