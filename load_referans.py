# load_referans.py
import os
import sys
import django
import pandas as pd
import unicodedata

# Django ayarlarını yükle
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insurance_project.settings")
django.setup()

from insurance_app.models import Referans  # Referans modelin

def normalize_column(col_name):
    """Sütun adlarını normalize et: Türkçe karakterleri İngilizce yap, boşlukları _ ile değiştir, büyük harf"""
    mapping = str.maketrans("İĞÜŞÖÇı", "IGUSOCi")
    normalized = unicodedata.normalize('NFKD', str(col_name)).translate(mapping)
    normalized = normalized.encode('ascii', 'ignore').decode('utf-8')
    return normalized.strip().replace(' ', '_').upper()

def load_referans(excel_path):
    try:
        df = pd.read_excel(excel_path, dtype=str)
        df.fillna("", inplace=True)

        # Kolon isimlerini normalize et
        df.columns = [normalize_column(col) for col in df.columns]

        # Gerekli sütunlar
        required_cols = ['ADI_SOYADI', 'POLICE_ADET', 'REFERANS', 'ACIKLAMA']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Excel’de eksik sütunlar: {', '.join(missing_cols)}")

        added_count = 0
        for _, row in df.iterrows():
            ad_soyadi = row.get('ADI_SOYADI', '').strip()
            police_adet = row.get('POLICE_ADET', '').strip()
            referans_text = row.get('REFERANS', '').strip()
            aciklama = row.get('ACIKLAMA', '').strip()

            if ad_soyadi:  # sadece isim varsa ekle
                # Önce aynı isimli kaydı kontrol et, tekrar eklemeyelim
                obj, created = Referans.objects.get_or_create(
                    ad_soyadi=ad_soyadi,
                    defaults={
                        'police_adet': police_adet,
                        'referans': referans_text,
                        'aciklama': aciklama
                    }
                )
                if created:
                    added_count += 1

        print(f">> {added_count} yeni referans başarıyla eklendi!")

    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python load_referans.py <excel_dosyasi.xlsx>")
        sys.exit(1)

    excel_path = sys.argv[1]
    load_referans(excel_path)
