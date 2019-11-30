from django.db.models import F
from django.forms import modelform_factory
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


# class NameForm(forms.ModelForm):
#     your_name = forms.CharField(label='Your name', max_length=100)

class StationOrderInlineFromSet(BaseInlineFormSet):

    def __init__(self, data=None, files=None, instance=None, save_as_new=False, prefix=None, queryset=None, **kwargs):
        if len(queryset) > 0:
            last_insatnce = queryset[len(queryset) - 1]
            last_station_id = last_insatnce.station_to_id
            StationOrder(station_from_id=last_station_id, station_to_id=last_station_id,
                         line_id=last_insatnce.line_id).save()
        super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)

    def __del__(self):
        StationOrder.objects.filter(station_from_id=F('station_to_id')).delete()

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     last_insatnce = queryset[len(queryset) - 1]
    #     last_station_id = last_insatnce.station_to_id
    #     StationOrder(station_from_id=last_station_id, station_to_id=last_station_id, line_id=last_insatnce.line_id).save()
    #     return super().get_queryset()

    # def __init__(self, data=None, files=None, instance=None, save_as_new=False, prefix=None, queryset=None, **kwargs):
    #     super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)
    #     self.extra_forms[0].instance.station_from_id = self.forms[-1].instance.station_to_id
    #     # self.extra_forms[0].instance.distance = self.forms[-1].instance.distance
    #     # self.extra_forms[0].fields['distance'].initial = 5 #self.forms[-1].instance.distance
    #     self.forms[-1].fields['station_from'].initial = self.forms[-1].instance.station_to_id
    #     self.forms[-1].fields['station_from'].show_hidden_initila = True
    #     # StationOrderForm = modelform_factory(StationOrder, exclude=('station_to',))
    #     # self.forms.append(
    #     #     StationOrderForm(instance=StationOrder(station_from_id=self.forms[-1].instance.station_to_id)))
    #     # for form in self.forms:
    #     #     print(form)
    #

    def save(self, commit=True):
        instances = super().save(False)
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

    # def __init__(self, model, admin_site):
    #
    #     # queryset = StationOrder.objects.filter(line_id=)
    #     # last_insatnce = queryset[len(queryset) - 1]
    #     # last_station_id = last_insatnce.station_to_id
    #     # StationOrder(station_from_id=last_station_id, station_to_id=last_station_id, line_id=last_insatnce.line_id).save()
    #     # return super().get_queryset()
    #     super().__init__(model, admin_site)

    def get_inline_instances(self, request, obj=None):
        inlines_edit = [ServiceInline, ]
        inlines_create = inlines_edit + [StationOrderInline, ]
        if obj:
            inlines = inlines_create  # inlines_edit
        else:
            inlines = inlines_create
        return [inline(self.model, self.admin_site) for inline in inlines]

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
