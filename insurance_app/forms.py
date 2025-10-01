from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Customer, Policy, PolicyType, Referans
import re

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['tc_id', 'name', 'phone_number', 'profession', 'date_of_birth', 'city']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'max': timezone.now().date()}),
            # maxlength'i 11'den 20 gibi daha büyük bir değere çıkarabilirsiniz,
            # ancak modeliniz 11 olduğu için şimdilik kalsın.
            'tc_id': forms.TextInput(attrs={'placeholder': '11 haneli TC kimlik numarası', 'maxlength': '11'}), 
            'phone_number': forms.TextInput(attrs={'placeholder': '05xxxxxxxxx', 'maxlength': '15'}),
        }

    def clean_tc_id(self):
        """
        TC geçerlilik kontrolü kaldırıldı. Sadece modelin max_length kısıtlamasına uyulur.
        """
        tc_id = self.cleaned_data.get('tc_id')
        # Bu kısım sadece boşlukları temizleyip değeri döndürür.
        if tc_id:
             return str(tc_id).strip()
        return tc_id

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone_clean = re.sub(r'[^\d]', '', phone)
            if len(phone_clean) == 11 and phone_clean.startswith('0'):
                if not phone_clean.startswith(('050', '051', '052', '053', '054', '055', '056', '057', '058', '059')):
                    raise ValidationError("Geçerli bir cep telefonu numarası giriniz.")
            elif len(phone_clean) == 10 and not phone_clean.startswith('0'):
                phone_clean = '0' + phone_clean
                if not phone_clean.startswith(('050', '051', '052', '053', '054', '055', '056', '057', '058', '059')):
                    raise ValidationError("Geçerli bir cep telefonu numarası giriniz.")
            else:
                raise ValidationError("Telefon numarası 10 veya 11 haneli olmalıdır.")
            return phone_clean
        return phone

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("İsim en az 2 karakter olmalıdır.")
            if not re.match(r"^[a-zA-ZçğıöşüÇĞIİÖŞÜ\s]+$", name):
                raise ValidationError("İsim sadece harflerden oluşmalıdır.")
        return name

    def clean_date_of_birth(self):
        birth_date = self.cleaned_data.get('date_of_birth')
        if birth_date:
            today = timezone.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if birth_date > today:
                raise ValidationError("Doğum tarihi gelecekte olamaz.")
            if age > 120:
                raise ValidationError("Geçerli bir doğum tarihi giriniz.")
            if age < 18:
                raise ValidationError("Müşteri en az 18 yaşında olmalıdır.")
        return birth_date


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['policy_type', 'insurance_company', 'plate_number', 'license_number', 'end_date']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'plate_number': forms.TextInput(attrs={'placeholder': '35 ABC 123', 'style': 'text-transform: uppercase'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Eğer POST ile gelen veride policy_type varsa, onun adına göre (kasko veya trafik) plate/license required ayarla.
        Bu sayede frontend/backend tutarlı olur.
        """
        super().__init__(*args, **kwargs)
        try:
            data = kwargs.get('data') or (args[0] if args else None)
            policy_type_id = None
            if data:
                # data bir QueryDict ise key 'policy_type' olacaktır
                policy_type_id = data.get('policy_type')
            if policy_type_id:
                pt = PolicyType.objects.filter(pk=policy_type_id).first()
                if pt and ('kasko' in pt.name.lower() or 'trafik' in pt.name.lower()):
                    self.fields['plate_number'].required = True
                    self.fields['license_number'].required = True
                else:
                    self.fields['plate_number'].required = False
                    self.fields['license_number'].required = False
        except Exception:
            # Hata olsa da form yüklenmeye devam etsin (debug sırasında log ekleyebilirsin)
            pass

    def clean_plate_number(self):
        plate = self.cleaned_data.get('plate_number')
        if plate:
            plate = plate.upper().strip()
            plate_pattern = r'^[0-9]{2}\s?[A-Z]{1,3}\s?[0-9]{1,4}$'
            if not re.match(plate_pattern, plate):
                raise ValidationError("Geçerli bir plaka formatı giriniz (örn: 35 ABC 123).")
        return plate

    def clean_license_number(self):
        license_num = self.cleaned_data.get('license_number')
        if license_num:
            license_num = license_num.strip()
            if len(license_num) < 3:
                raise ValidationError("Ruhsat numarası en az 3 karakter olmalıdır.")
        return license_num

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date:
            today = timezone.now().date()
            if end_date <= today:
                raise ValidationError("Poliçe bitiş tarihi bugünden sonra olmalıdır.")
            if end_date > today.replace(year=today.year + 5):
                raise ValidationError("Poliçe bitiş tarihi çok uzak gelecekte.")
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        policy_type = cleaned_data.get('policy_type')
        plate_number = cleaned_data.get('plate_number')

        # Burada parantezler önemli — önce policy_type kontrolü, sonra isim kontrolü
        if policy_type and ('kasko' in policy_type.name.lower() or 'trafik' in policy_type.name.lower()):
            if not plate_number:
                raise ValidationError({'plate_number': 'Bu poliçe türü için plaka numarası zorunludur.'})

        return cleaned_data

class ReferenceUploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel Dosyası Seç")




class ReferansForm(forms.ModelForm):
    class Meta:
        model = Referans
        fields = ['ad_soyadi', 'police_adet', 'referans', 'aciklama']
        widgets = {
            'ad_soyadi': forms.TextInput(attrs={'class': 'form-control'}),
            'police_adet': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'referans': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    