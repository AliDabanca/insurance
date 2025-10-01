# insurance_app/admin.py
from django.contrib import admin
from .models import Customer, Policy, PolicyType, InsuranceCompany

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('tc_id', 'name', 'phone_number', 'profession', 'date_of_birth', 'city')
    search_fields = ('name', 'tc_id', 'phone_number')
    list_filter = ('city', 'profession') # Şehir ve mesleğe göre filtreleme ekledik

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('customer', 'policy_type', 'insurance_company', 'plate_number', 'license_number', 'end_date')
    list_filter = ('policy_type', 'insurance_company', 'end_date')
    search_fields = ('customer__name', 'customer__tc_id', 'plate_number', 'license_number') # Müşteri TC'si ile de aranabilir
    raw_id_fields = ('customer',) # Büyük veri setlerinde müşteri seçimi için daha performanslı

@admin.register(PolicyType)
class PolicyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)