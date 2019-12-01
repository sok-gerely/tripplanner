import modelclone
from django.core.exceptions import ValidationError
from django.db.models import F
from django.forms import modelform_factory, ModelForm
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

# class StationOrderForm(ModelForm):
#     class Meta:
#         model = StationOrder
#         fields = ('station_from', 'distance')


class StationOrderInlineFromSet(BaseInlineFormSet):
    # form = StationOrderForm

    def __init__(self, data=None, files=None, instance=None, save_as_new=False, prefix=None, queryset=None, **kwargs):
        self.is_validation_happening = False
        StationOrderInlineFromSet.station_order_clean_up()
        instance_query = StationOrder.objects.filter(line=instance).all()
        if len(instance_query) > 0:
            last_insatnce = instance_query[len(instance_query) - 1]
            last_station_id = last_insatnce.station_to_id
            tmp_instance = StationOrder(station_from_id=last_station_id, station_to_id=last_station_id,
                         line_id=instance.id, distance=0) #
            # print(tmp_instance.clean_fields())
            # print(tmp_instance.clean())
            # print(tmp_instance.validate_unique())
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

    # def total_form_count(self):
    #     form_count = super().total_form_count()
    #     if self.is_validation_happening:
    #         if form_count > 0:
    #             return form_count - 1
    #         else:
    #             return 0
    #     else:
    #         return form_count

    # def full_clean(self):
    #     self.is_validation_happening = True
    #     super().full_clean()
    #     self.is_validation_happening = False

    def is_valid(self):
        # self.is_validation_happening = True
        # for form in self.forms:
            # form.cleaned_data = form.clean()
        # self.forms[self.initial_form_count() - 1]._errors = {}
        # print(self.forms[self.initial_form_count()-1]._errors)
        res = super().is_valid()
        # self._errors = [{} for _ in self._errors]
        # self.is_validation_happening = False
        print(self.forms[self.initial_form_count() - 1].cleaned_data)
        # self._errors[self.initial_form_count()-1] = {}
        return True # res

    #
    # def clean(self):
    #     # self.is_validation_happening = True
    #     # self._errors = [{} for _ in self._errors]
    #     res = super().clean()
    #     # for form in self.forms:
    #     #     form._errors = {}
    #     # self.is_validation_happening = False
    #     return res

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
        print('Saving')
        super().save(False)
        # instances = list(StationOrder.objects.all())
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


class StationOrderInlineEdit(admin.TabularInline):
    model = StationOrder
    fk_name = "line"
    # readonly_fields = ('station_from',)
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


class LineAdmin(modelclone.ClonableModelAdmin):
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
        inlines_edit = [ServiceInline, StationOrderInlineEdit]
        inlines_create = [ServiceInline, StationOrderInline]
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
    search_fields = ['name']
    list_display = ('name',)


admin.site.register(Station, StationAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TimetableData, TimetableDataAdmin)
