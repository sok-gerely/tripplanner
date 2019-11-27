import modelclone
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

    def save(self, commit=True):
        instances = super().save(False)
        for next, current in zip(instances[1:], instances):
            current.station_to = next.station_from
            if commit:
                current.save()
        if len(instances):
            instances.pop()
        return instances

    def clean(self):
        for form in self.forms:
            print(form)


class StationOrderInline(admin.TabularInline):
    model = StationOrder
    fk_name = "line"
    exclude = ('station_to',)
    extra = 0
    formset = StationOrderInlineFromSet
    # form = NameForm


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


class LineAdmin(modelclone.ClonableModelAdmin):

    def get_inline_instances(self, request, obj=None):
        inlines_edit = [ServiceInline, ]
        inlines_create = inlines_edit + [StationOrderInline, ]
        if obj:
            inlines = inlines_edit
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
    list_display = ('name',)


admin.site.register(Station, StationAdmin)
admin.site.register(Line, LineAdmin)
