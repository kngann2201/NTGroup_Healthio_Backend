from django.contrib import admin
from django.urls import path
from django.utils.safestring import mark_safe
from healthio import models
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ExerciseForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = models.Exercise
        fields = '__all__'

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'health_goals', 'MET')
    search_fields = ['name']
    list_filter = ['health_goal']
    form = ExerciseForm

    def health_goals(self, obj):
        return ", ".join(hg.name for hg in obj.health_goal.all())

class CustomerInlineAdmin(admin.StackedInline):
    model = models.Customer
    fk_name = 'user'

class ExpertInlineAdmin(admin.StackedInline):
    model = models.Expert
    fk_name = 'user'

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'role')
    search_fields = ['first_name', 'last_name']
    list_filter = ['role']
    readonly_fields = ['image_view']
    def image_view(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="100" height="100" />')
        return ""

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj:
            if obj.role == 1:
                inlines = [CustomerInlineAdmin(self.model, self.admin_site)]
            else:
                inlines = [ExpertInlineAdmin(self.model, self.admin_site)]
        return inlines

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

        if not change:
            if obj.role==1:
                models.Customer.objects.get_or_create(user=obj)
            elif obj.role == 2:
                models.Expert.objects.get_or_create(user=obj)

class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'expert')

class AppAdminSite(admin.AdminSite):
    site_header = 'HEALTHIO WITH US'

    def get_urls(self):
        return [path('stats-view', self.stats_view)] + super().get_urls()

    def stats_view(self, request):
        exercise = models.Exercise.objects.all()
        count = models.Exercise.objects.filter(is_custom=False).count()
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/stats.html', {'count': count, 'exercise': exercise})

admin_site = AppAdminSite(name='myadmin')
admin_site.register(models.Exercise, ExerciseAdmin)
admin_site.register(models.User, UserAdmin)
admin_site.register(models.Contract, ContractAdmin)
admin_site.register(models.Feedback)
admin_site.register(models.Request)
admin_site.register(models.HealthGoal)
admin_site.register(models.HealthRecord)
admin_site.register(models.Record)
admin_site.register(models.Reminder)
admin_site.register(models.Schedule)
admin_site.register(models.Practice)
admin_site.register(models.PracticeDetail)
admin_site.register(models.Meal)
admin_site.register(models.MealDetail)
admin_site.register(models.ExerciseSample)
admin_site.register(models.DishSample)



