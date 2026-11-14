"""BasinShift — Tüm Arayüzleri Çekme Scripti."""
import os
import shutil
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler"
BACKUP_DIR = r"c:\Users\yunus\Desktop\spaceapps\basinshift\mevcutarayuzler"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def wait_loading(page, extra=2):
    try:
        page.wait_for_selector(".stSpinner", state="detached", timeout=30000)
    except Exception:
        pass
    time.sleep(extra)


def take_full_screenshot(page, filename, description=""):
    print(f"[{description}] Yakalanıyor: {filename}...")
    wait_loading(page)
    h = page.evaluate('document.querySelector("#stMain") ? document.querySelector("#stMain").scrollHeight : 1080')
    page.set_viewport_size({"width": 1920, "height": max(h, 1080)})
    time.sleep(1)
    
    out_path = os.path.join(OUTPUT_DIR, filename)
    page.screenshot(path=out_path)
    shutil.copy(out_path, os.path.join(BACKUP_DIR, filename))
    print(f"[{description}] Kaydedildi (Boyut: 1920x{max(h, 1080)})")


def run():
    # Remove old test files
    for f in os.listdir(OUTPUT_DIR):
        if f.startswith("test_"):
            try:
                os.remove(os.path.join(OUTPUT_DIR, f))
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # ----------------------------------------------------
        # 1. TARLA (GİRİŞ & YAPILANDIRMA)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/", wait_until="networkidle")
        wait_loading(page, 3)
        take_full_screenshot(page, "01_tarla_girisi_ve_yapilandirma.png", "Tarla Girişi")

        # 1b. Kenar çubuğu veri kaynakları açık görünümü
        try:
            exp = page.locator('[data-testid="stSidebar"] summary:has-text("Veri kaynakları")')
            if exp.count() > 0:
                exp.click()
                time.sleep(1)
                take_full_screenshot(page, "02_tarla_veri_kaynaklari_paneli.png", "Sidebar Veri Kaynakları")
        except Exception as e:
            print("Veri kaynakları açılamadı:", e)

        # ----------------------------------------------------
        # 2. İKLİM GEÇMİŞİ (STATUS)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/status", wait_until="networkidle")
        wait_loading(page, 3)
        take_full_screenshot(page, "03_iklim_gecmisi_ve_risk_analizi.png", "İklim Geçmişi & Risk")

        # ----------------------------------------------------
        # 3. EKİM PLANLARI (PLANS)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/plans", wait_until="networkidle")
        wait_loading(page, 4)
        take_full_screenshot(page, "04_ekim_planlari_karsilastirma.png", "Ekim Planları Karşılaştırma")

        # 3b. Neden bu plan açıklamaları açık
        try:
            whys = page.locator('summary:has-text("Neden bu plan?")')
            count = whys.count()
            for i in range(count):
                whys.nth(i).click()
            time.sleep(1)
            take_full_screenshot(page, "05_ekim_planlari_neden_aciklamalari.png", "Planlar Neden Açıklamaları")
        except Exception as e:
            print("Neden bu plan açılamadı:", e)

        # 3c. Pareto analizi açık
        try:
            pareto = page.locator('summary:has-text("Tüm uygun planlar")')
            if pareto.count() > 0:
                pareto.click()
                time.sleep(2)
                take_full_screenshot(page, "06_ekim_planlari_pareto_analizi.png", "Pareto ve Tüm Planlar")
        except Exception as e:
            print("Pareto açılamadı:", e)

        # ----------------------------------------------------
        # 4. İKİ GELECEK (FUTURES)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/futures", wait_until="networkidle")
        wait_loading(page, 3)
        take_full_screenshot(page, "07_iki_gelecek_dengeli_senaryo.png", "İki Gelecek - Denge")

        # 4b. Akifer odaklı senaryo
        try:
            akifer_radio = page.locator('label:has-text("Akifer")')
            if akifer_radio.count() > 0:
                akifer_radio.first.click()
                time.sleep(2)
                take_full_screenshot(page, "08_iki_gelecek_akifer_senaryo.png", "İki Gelecek - Akifer")
        except Exception as e:
            print("Akifer seçilemedi:", e)

        # 4c. Kâr odaklı senaryo
        try:
            kar_radio = page.locator('label:has-text("Kâr")')
            if kar_radio.count() > 0:
                kar_radio.first.click()
                time.sleep(2)
                take_full_screenshot(page, "09_iki_gelecek_kar_senaryo.png", "İki Gelecek - Kâr")
        except Exception as e:
            print("Kâr seçilemedi:", e)

        # ----------------------------------------------------
        # 5. HAVZA GÖRÜNÜMÜ (BASIN)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/basin", wait_until="networkidle")
        wait_loading(page, 4)
        take_full_screenshot(page, "10_havza_gorunumu_ve_anarsi_maliyeti.png", "Havza Görünümü")

        # ----------------------------------------------------
        # 6. KARNE & RAPOR (REPORT)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/report", wait_until="networkidle")
        wait_loading(page, 3)
        # Çiftçi adı yazalım
        try:
            name_input = page.locator('input[type="text"]').first
            name_input.fill("Mehmet Amca")
            name_input.press("Enter")
            time.sleep(1)
        except Exception:
            pass
        take_full_screenshot(page, "11_ciftci_karnesi_denge_raporu.png", "Çiftçi Karnesi - Denge")

        # 6b. Mevcut plan karne görünümü
        try:
            mevcut_radio = page.locator('label:has-text("Mevcut planınız")')
            if mevcut_radio.count() > 0:
                mevcut_radio.first.click()
                time.sleep(2)
                take_full_screenshot(page, "12_ciftci_karnesi_mevcut_plan.png", "Çiftçi Karnesi - Mevcut Plan")
        except Exception as e:
            print("Mevcut plan karne açılamadı:", e)

        # ----------------------------------------------------
        # 7. YÖNTEM VE VERİLER (METHOD)
        # ----------------------------------------------------
        page.goto("http://localhost:8501/method", wait_until="networkidle")
        wait_loading(page, 3)
        take_full_screenshot(page, "13_yontem_ve_veri_kaynaklari.png", "Yöntem & Veri Kaynakları")

        # 7b. Sözlük maddeleri açılmış görünüm
        try:
            terms = page.locator('summary:has-text("Referans"), summary:has-text("Pareto"), summary:has-text("Suyun gölge"), summary:has-text("Koordinasyonsuzluğun")')
            for i in range(terms.count()):
                terms.nth(i).click()
            time.sleep(1)
            take_full_screenshot(page, "14_yontem_sozluk_detaylari.png", "Yöntem Sözlük Detayları")
        except Exception as e:
            print("Sözlük detayları açılamadı:", e)

        # ----------------------------------------------------
        # 8. İNGİLİZCE ARAYÜZ (ENGLISH VERSION)
        # ----------------------------------------------------
        try:
            en_radio = page.locator('[data-testid="stSidebar"] label:has-text("English")')
            if en_radio.count() > 0:
                en_radio.first.click()
                time.sleep(2)
                page.goto("http://localhost:8501/plans", wait_until="networkidle")
                wait_loading(page, 3)
                take_full_screenshot(page, "15_ingilizce_planlar_dashboard.png", "English Plans Dashboard")
                # Dil'i tekrar Türkçe yapalım
                tr_radio = page.locator('[data-testid="stSidebar"] label:has-text("Türkçe")')
                if tr_radio.count() > 0:
                    tr_radio.first.click()
                    time.sleep(1)
        except Exception as e:
            print("İngilizce görünüm yakalanamadı:", e)

        browser.close()
        print("\n=== TÜM ARAYÜZLER BAŞARIYLA ÇEKİLDİ! ===")


if __name__ == "__main__":
    run()
