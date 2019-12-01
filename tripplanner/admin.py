from django.core.exceptions import ValidationError
from django.db.models import F
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.forms.models import ModelForm, BaseInlineFormSet

from .models import Station, Line, StationOrder, Service, TimetableData, Delay

admin.site.unregister(Group)
admin.site.unregister(User)


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""
        return True


class StationOrderInlineFromSet(BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None, save_as_new=False, prefix=None, queryset=None, **kwargs):
        self.is_validation_happening = False
        StationOrderInlineFromSet.station_order_clean_up()
        instance_query = StationOrder.objects.filter(line=instance).all()
        if len(instance_query) > 0:
            last_insatnce = instance_query[len(instance_query) - 1]
            last_station_id = last_insatnce.station_to_id
            tmp_instance = StationOrder(station_from_id=last_station_id, station_to_id=last_station_id,
                         line_id=instance.id, distance=0)
            try:
                tmp_instance.full_clean()
            except ValidationError as e:
                print(e)
            tmp_instance.save()
        queryset = StationOrder.objects.all()
        super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)

    def __del__(self):
        self.station_order_clean_up()

    @staticmethod
    def station_order_clean_up():
        StationOrder.objects.filter(station_to_id=F('station_from_id')).delete()

    def is_valid(self):
        super().is_valid()
        return not sum([k != 'id' for error in self.errors for k in error.keys()]) # sum([len(error) for error in self.errors]) # <= 1  # res # True

    def save(self, commit=True):
        super().save(False)
        instances = [form.instance for form in self.forms if form not in self.deleted_forms]
        for form in self.deleted_forms:
            if form.instance.pk is not None:
                self.delete_existing(form.instance, commit)
        for next, current in zip(instances[1:], instances):
            current.station_to = next.station_from
            if commit:
                current.save()
        if len(instances):
            instances.pop()
        return instances


class StationOrderInline(admin.TabularInline):
    autocomplete_fields = ['station_from']
    model = StationOrder
    fk_name = "line"
    exclude = ('station_to',)
    extra = 0
    formset = StationOrderInlineFromSet


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    show_change_link = True
    form = AlwaysChangedModelForm


class DelayInline(admin.TabularInline):
    model = Delay
    extra = 0


class TimetableDataInline(admin.TabularInline):
    model = TimetableData
    fk_name = "service"
    readonly_fields = ('station',)
    fields = ('station', 'date_time',)
    extra = 0
    max_num = model.station_num
    can_delete = False
    show_change_link = True


class LineAdmin(admin.ModelAdmin):
    save_as = True

    inlines = [ServiceInline, StationOrderInline]

    list_display = ('name', 'type',)
    list_filter = ('type',)


class ServiceAdmin(admin.ModelAdmin):
    inlines = [
        TimetableDataInline,
    ]
    list_display = ('line', 'departure_time', 'type', 'valid_from', 'valid_until', 'fee')
    list_filter = ('line', 'type', 'valid_from', 'valid_until',)


class TimetableDataAdmin(admin.ModelAdmin):
    inlines = [
        DelayInline,
    ]
    readonly_fields = ('station',)
    list_display = ('service', 'station', 'date_time',)
    list_filter = ('service', 'station',)


class StationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name',)


admin.site.register(Station, StationAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TimetableData, TimetableDataAdmin)
