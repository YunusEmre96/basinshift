"""
BasinShift Kılavuzu Master Üretici Betiği (65 Sayfalık Kapsamlı Dokümantasyon)
NASA Space Apps Challenge 2026 Tasarım Sistemi & Canlı Veri Doğrulaması
"""
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from pdf_builder import BasinShiftPDF
from pages_01_15 import render_pages_01_15
from pages_16_30 import render_pages_16_30
from pages_31_45 import render_pages_31_45
from pages_46_65 import render_pages_46_65


def main():
    print("=" * 70)
    print("BASINSHIFT KILAVUZU 65 SAYFALIK MASTER PDF ÜRETİMİ BAŞLATILIYOR")
    print("=" * 70)
    
    t0 = time.time()
    pdf = BasinShiftPDF()
    pdf.alias_nb_pages()
    
    print("[1/4] Sayfa 01 - 15 derleniyor (Kapak, İçindekiler, Bölüm 1, 2, 3, 4.1-4.4)...")
    render_pages_01_15(pdf)
    
    print("[2/4] Sayfa 16 - 30 derleniyor (Bölüm 4.5-4.6, 5, 6, 7, 8.1-8.3)...")
    render_pages_16_30(pdf)
    
    print("[3/4] Sayfa 31 - 45 derleniyor (Bölüm 8.4-8.8, 9, 10.1-10.2)...")
    render_pages_31_45(pdf)
    
    print("[4/4] Sayfa 46 - 65 derleniyor (Bölüm 10.3, 11, 12, 13, Ek A, Ek B)...")
    render_pages_46_65(pdf)
    
    output_pdf_path = r"c:\Users\yunus\Desktop\spaceapps\BasinShift_Kilavuz.pdf"
    print(f"\nPDF diske yazılıyor: {output_pdf_path}...")
    pdf.output(output_pdf_path)
    
    elapsed = time.time() - t0
    total_pages = pdf.page_no()
    file_size_mb = os.path.getsize(output_pdf_path) / (1024 * 1024)
    
    print("=" * 70)
    print(f"BAŞARIYLA TAMAMLANDI!")
    print(f"Toplam Sayfa Sayısı: {total_pages} Sayfa")
    print(f"Dosya Boyutu:        {file_size_mb:.2f} MB")
    print(f"Harcanan Süre:       {elapsed:.2f} saniye")
    print("=" * 70)


if __name__ == "__main__":
    main()
