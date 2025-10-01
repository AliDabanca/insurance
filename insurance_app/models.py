from django.db import models

class Customer(models.Model):
    tc_id = models.CharField(max_length=20, unique=False, null=True, blank=True, verbose_name="TC Kimlik No") 
    name = models.CharField(max_length=255, verbose_name="Adı Soyadı")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon Numarası")
    profession = models.CharField(max_length=100, blank=True, null=True, verbose_name="Meslek")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Doğum Tarihi")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Şehir")

    def __str__(self):
        return self.name

class PolicyType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Poliçe Tipi")

    def __str__(self):
        return self.name

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Sigorta Şirketi")

    def __str__(self):
        return self.name

class Policy(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='policies', verbose_name="Müşteri")
    policy_type = models.ForeignKey(PolicyType, on_delete=models.CASCADE, verbose_name="Poliçe Tipi")
    insurance_company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, verbose_name="Sigorta Şirketi")
    plate_number = models.CharField(max_length=20, blank=False, null=False ,verbose_name="Plaka Numarası")
    license_number = models.CharField(max_length=50, blank=False, null=False, verbose_name="Ruhsat Numarası")
    end_date = models.DateField(blank=True, null=True, verbose_name="Bitiş Tarihi")

    def __str__(self):
        return f"{self.policy_type.name} - {self.customer.name}"
    
    



class Referans(models.Model):
    ad_soyadi = models.CharField(max_length=255)
    police_adet = models.CharField(max_length=50, blank=True)
    referans = models.CharField(max_length=255, blank=True)
    aciklama = models.TextField(blank=True)

    def __str__(self):
        return self.ad_soyadi