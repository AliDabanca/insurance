from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from insurance_app.models import Customer, PolicyType, InsuranceCompany, Policy
from django.db import transaction, IntegrityError
import unicodedata
import numpy as np # pandas ile NaN kontrolü için eklendi

class Command(BaseCommand):
    help = 'Belirtilen Excel dosyasındaki müşteri ve poliçe verilerini import eder.'

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str, help='Excel dosyasının yolu')

    # ESKİDE TC KONTROLÜ YAPAN _is_valid_tc METODU KALDIRILDI.

    def _normalize_column_name(self, col_name):
        
        normalized = unicodedata.normalize('NFKD', col_name).encode('ascii', 'ignore').decode('utf-8')
        return normalized.strip().replace(' ', '_').upper()

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        
        # =========================================================
        # KRİTİK BÖLÜM: TAMAMEN YENİLEME (ÖNCEKİ VERİYİ SİLME)
        # =========================================================
        self.stdout.write(self.style.WARNING('Mevcut tüm Müşteri ve Poliçe verileri siliniyor...'))

        try:
            policy_count = Policy.objects.all().count()
            Policy.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'{policy_count} adet eski poliçe kaydı silindi.'))

            customer_count = Customer.objects.all().count()
            Customer.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'{customer_count} adet eski müşteri kaydı silindi.'))

        except Exception as e:
            raise CommandError(f"Hata: Eski veriler silinirken bir sorun oluştu: {e}")

        # =========================================================
        # EXCEL OKUMA İŞLEMİ
        # =========================================================
        try:
            df = pd.read_excel(excel_path, dtype=str)
        except FileNotFoundError:
            raise CommandError(f"Hata: Excel dosyası bulunamadı: {excel_path}")
        except Exception as e:
            raise CommandError(f"Excel dosyası okunurken bir hata oluştu: {e}")

        self.stdout.write(self.style.NOTICE(f"Excel dosyasındaki orijinal sütunlar: {df.columns.tolist()}"))
        df.columns = [self._normalize_column_name(col) for col in df.columns]
        self.stdout.write(self.style.NOTICE(f"İşlenmiş sütunlar: {df.columns.tolist()}"))

        required_cols_for_check = [
            'MUSTERI', 'TC', 'POLICE', 'SIGORTA_SIRKETI', 'TARIH',
            'PLAKA', 'RUHSAT', 'DOGUM_TARIHI', 'SEHIR', 'TELEFON', 'MESLEK'
        ]
        
        missing_cols_in_excel = [col for col in required_cols_for_check if col not in df.columns]
        if missing_cols_in_excel:
            raise CommandError(
                f"Hata: Excel dosyasında beklenen bazı sütunlar bulunamadı. "
                f"Eksik sütunlar (normalize edilmiş): {', '.join(missing_cols_in_excel)}"
            )

        added_customers = 0
        added_policies = 0
        processed_rows = 0

        # =========================================================
        # VERİ EKLEME İŞLEMİ (TC Kontrolü Atlandı)
        # =========================================================
        for idx, row in df.iterrows():
            processed_rows += 1
            try:
                with transaction.atomic():
                    # ---- Müşteri Bilgileri ----
                    tc_id_raw = row.get('TC')
                    
                    # YENİ MANTIK: TC'yi sadece boşluklardan temizle ve kullan. Geçerlilik kontrolü YOK.
                    tc_id_for_customer = None
                    if pd.notna(tc_id_raw):
                        tc_id_for_customer = str(tc_id_raw).strip()
                    
                    # Eğer TC tamamen boşsa veya NaN ise, atlama (TC zorunlu bir alan ise hata verir)
                    # Burayı MÜŞTERİ MODELİNDE TC_ID ALANININ UNIQUE VE BLANK=FALSE OLMASINA GÖRE DÜZENLEYİN
                    if not tc_id_for_customer:
                         # TC boşsa 'Bilinmeyen TC' gibi bir varsayılan değer atayabiliriz 
                         # veya satırı atlayabiliriz. Varsayalım ki boş olamaz:
                         self.stderr.write(self.style.ERROR(
                             f"Hata: Satır {idx + 2} için eksik TC Kimlik No. Müşteri ve poliçe kaydı atlanıyor."
                         ))
                         continue # TC boşsa poliçe eklenemeyeceği için satırı atla
                    
                    name = str(row.get('MUSTERI', '')).strip()
                    if not name:
                        name = "Bilinmeyen Müşteri"

                    phone_number = str(row.get('TELEFON', '')).strip()
                    profession = str(row.get('MESLEK', '')).strip()
                    city = str(row.get('SEHIR', '')).strip()

                    birth_date = None
                    dob_raw = row.get('DOGUM_TARIHI')
                    if pd.notna(dob_raw):
                        try:
                            birth_date = pd.to_datetime(dob_raw, dayfirst=True, errors='coerce').date()
                        except Exception:
                            birth_date = None
                    
                    # update_or_create ile TC'ye göre müşteri eklenir (veya güncellenir)
                    customer, created = Customer.objects.update_or_create(
                        tc_id=tc_id_for_customer,
                        defaults={
                            'name': name,
                            'phone_number': phone_number if phone_number else None,
                            'profession': profession if profession else None,
                            'city': city if city else None,
                            'date_of_birth': birth_date
                        }
                    )
                    if created:
                        added_customers += 1
                        self.stdout.write(self.style.SUCCESS(f"Yeni müşteri eklendi: {customer.name} (TC: {customer.tc_id})"))
                    
                    # ---- Poliçe Bilgileri ----
                    policy_type_name = str(row.get('POLICE', '')).strip() or "BİLİNMEYEN POLİÇE"
                    policy_type, _ = PolicyType.objects.get_or_create(name=policy_type_name)

                    company_name = str(row.get('SIGORTA_SIRKETI', '')).strip() or "BİLİNMEYEN ŞİRKET"
                    insurance_company, _ = InsuranceCompany.objects.get_or_create(name=company_name)

                    plate_number = str(row.get('PLAKA', '')).strip() or "Bilinmeyen Plaka"
                    license_number = str(row.get('RUHSAT', '')).strip() or "Bilinmeyen Ruhsat"
                    
                    end_date = None
                    end_date_raw = row.get('TARIH')
                    if pd.notna(end_date_raw):
                        try:
                            end_date = pd.to_datetime(end_date_raw, dayfirst=True, errors='coerce').date()
                        except Exception:
                            end_date = None

                    policy, created_policy = Policy.objects.update_or_create(
                        customer=customer,
                        policy_type=policy_type,
                        insurance_company=insurance_company,
                        plate_number=plate_number,
                        defaults={
                            'license_number': license_number,
                            'end_date': end_date
                        }
                    )
                    if created_policy:
                        added_policies += 1
                        self.stdout.write(self.style.SUCCESS(f"Yeni poliçe eklendi: {policy.policy_type.name} - {policy.customer.name}"))
            
            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(
                    f"Veritabanı hatası: Satır {idx + 2} işlenirken bir veri bütünlüğü hatası oluştu: {e}"
                ))
                self.stderr.write(f"Sorunlu satır verileri (ham): {row.to_dict()}")
                continue
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"Hata: {idx + 2}. satır işlenirken beklenmeyen bir hata oluştu: {e}"
                ))
                self.stderr.write(f"Sorunlu satır verileri (ham): {row.to_dict()}")
                continue
                
        self.stdout.write(self.style.SUCCESS("-" * 50))
        self.stdout.write(self.style.SUCCESS("Tüm işlemler tamamlandı."))
        self.stdout.write(self.style.SUCCESS(f"Toplam {added_customers} yeni müşteri ve {added_policies} yeni poliçe eklendi."))
        self.stdout.write(self.style.NOTICE(f"{processed_rows} satır işlendi."))