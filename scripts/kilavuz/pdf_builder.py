"""
BasinShift Kılavuzu PDF Motoru
NASA Space Apps Challenge 2026 Tasarım İlkelerine Uygun Modern PDF Motoru
"""
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

# Space Apps 2026 Resmi Renk Paleti
NAVY = (7, 23, 63)         # #07173F - Deep Space Navy
CADET = (13, 27, 71)       # #0D1B47 - Space Cadet
BLUE = (0, 66, 166)        # #0042A6 - Electric Blue
YELLOW = (234, 254, 7)     # #EAFE07 - Neon Yellow
RED = (228, 55, 0)         # #E43700 - Rocket Red
GREEN = (16, 149, 93)      # #10955D - Verified Emerald Green
AMBER = (217, 119, 6)      # #D97706 - Warning Amber
SLATE_DARK = (30, 41, 59)  # #1E293B - Body Text
SLATE_MED = (71, 85, 105)  # #475569 - Secondary Text
SLATE_LIGHT = (148, 163, 184) # #94A3B8 - Subtle borders & muted
BG_LIGHT = (248, 250, 252)
BG_CARD = (241, 245, 249)
BORDER_COLOR = (226, 232, 240)

FONT_REG = r"C:\Users\yunus\Desktop\spaceapps\basinshift\.venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\DejaVuSans.ttf"
FONT_BOLD = r"C:\Users\yunus\Desktop\spaceapps\basinshift\.venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\DejaVuSans-Bold.ttf"
FONT_OBL = r"C:\Users\yunus\Desktop\spaceapps\basinshift\.venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\DejaVuSans-Oblique.ttf"
FONT_BOLDOBL = r"C:\Users\yunus\Desktop\spaceapps\basinshift\.venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\DejaVuSans-BoldOblique.ttf"


class BasinShiftPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=15)
        
        # Font yükleme
        self.add_font("DejaVu", "", FONT_REG)
        self.add_font("DejaVu", "B", FONT_BOLD)
        self.add_font("DejaVu", "I", FONT_OBL)
        self.add_font("DejaVu", "BI", FONT_BOLDOBL)
        
        self.current_chapter = ""
        self.fig_counter = 0

    def header(self):
        if self.page_no() > 1:
            self.set_font("DejaVu", "", 7.5)
            self.set_text_color(*SLATE_MED)
            self.cell(90, 5, "NASA Space Apps Challenge 2026 · BasinShift", border=0, align="L")
            chap_text = self.current_chapter if self.current_chapter else "Sistem Dokümantasyonu & Kullanım Kılavuzu"
            self.cell(0, 5, chap_text, border=0, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(*BORDER_COLOR)
            self.set_line_width(0.3)
            self.line(16, self.get_y(), 194, self.get_y())
            self.ln(2.5)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12)
            self.set_draw_color(*BORDER_COLOR)
            self.set_line_width(0.3)
            self.line(16, self.get_y(), 194, self.get_y())
            self.set_font("DejaVu", "", 7.5)
            self.set_text_color(*SLATE_MED)
            self.cell(90, 5, "BasinShift · Saha Dönüşümü Karar Destek Aracı v2.0 (Resmi NASA Verili)", border=0, align="L")
            self.cell(0, 5, f"Sayfa {self.page_no()} / {{nb}}", border=0, align="R")

    def add_exact_page(self, chapter_title=""):
        if chapter_title:
            self.current_chapter = chapter_title
        self.add_page()

    def chapter_title(self, num_str, title, subtitle):
        self.current_chapter = f"Bölüm {num_str} · {title}"
        
        # Bölüm Numarası Rozeti (Derin Lacivert zemin, Neon Sarı sol vurgu)
        badge_y = self.get_y()
        self.set_fill_color(*NAVY)
        self.rect(16, badge_y, 16, 12, "F")
        self.set_fill_color(*YELLOW)
        self.rect(16, badge_y, 2, 12, "F")
        
        self.set_xy(17, badge_y + 1)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(14, 10, num_str, align="C")
        
        # Başlık
        self.set_xy(36, badge_y)
        self.set_font("DejaVu", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Alt Başlık
        self.set_x(36)
        self.set_font("DejaVu", "I", 8.8)
        self.set_text_color(*SLATE_MED)
        self.multi_cell(142, 4.2, subtitle)
        
        # Dekoratif çizgi
        self.ln(2.5)
        sep_y = self.get_y()
        self.set_draw_color(*BLUE)
        self.set_line_width(0.8)
        self.line(16, sep_y, 45, sep_y)
        self.set_draw_color(*BORDER_COLOR)
        self.set_line_width(0.3)
        self.line(45, sep_y, 194, sep_y)
        self.ln(3.5)

    def section_title(self, title):
        sy = self.get_y()
        self.set_fill_color(*BLUE)
        self.rect(16, sy + 0.5, 2.5, 5, "F")
        
        self.set_xy(20, sy)
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(*NAVY)
        self.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)

    def subsection_title(self, title):
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(*BLUE)
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def body(self, text, space=2.0):
        self.set_font("DejaVu", "", 8.2)
        self.set_text_color(*SLATE_DARK)
        self.multi_cell(0, 4.1, text)
        if space > 0:
            self.ln(space)

    def bullet(self, prefix, text, space=1.5):
        self.set_font("DejaVu", "B", 8.2)
        self.set_text_color(*BLUE)
        self.cell(4, 4.1, "•", align="R")
        self.set_x(22)
        if prefix:
            self.cell(self.get_string_width(prefix + " "), 4.1, prefix + " ")
            self.set_font("DejaVu", "", 8.2)
            self.set_text_color(*SLATE_DARK)
            self.multi_cell(0, 4.1, text)
        else:
            self.set_font("DejaVu", "", 8.2)
            self.set_text_color(*SLATE_DARK)
            self.multi_cell(0, 4.1, text)
        if space > 0:
            self.ln(space)

    def callout(self, title, text, kind="info"):
        color_map = {
            "info": ((239, 246, 255), BLUE),
            "verified": ((236, 253, 245), GREEN),
            "warning": ((255, 251, 235), AMBER),
            "danger": ((254, 242, 242), RED),
        }
        bg, border = color_map.get(kind, ((248, 250, 252), BLUE))
        
        words = text.split()
        approx_lines = max(1, len(" ".join(words)) // 105 + 1)
        box_h = 6 + (approx_lines * 3.8)
        
        box_y = self.get_y()
        self.set_fill_color(*bg)
        self.rect(16, box_y, 178, box_h, "F")
        self.set_fill_color(*border)
        self.rect(16, box_y, 2.5, box_h, "F")
        
        self.set_xy(21, box_y + 1.5)
        self.set_font("DejaVu", "B", 8)
        self.set_text_color(*border)
        self.cell(0, 4, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_x(21)
        self.set_font("DejaVu", "", 7.6)
        self.set_text_color(*SLATE_DARK)
        self.multi_cell(168, 3.6, text)
        
        self.set_y(box_y + box_h + 2)

    def metrics(self, items):
        n = len(items)
        gap = 2.5
        card_w = (178 - (gap * (n - 1))) / n
        card_h = 15
        start_y = self.get_y()
        
        for i, (val, label, note, color) in enumerate(items):
            cx = 16 + i * (card_w + gap)
            self.set_fill_color(*BG_CARD)
            self.rect(cx, start_y, card_w, card_h, "F")
            
            # Üst ince renkli çizgi
            self.set_fill_color(*color)
            self.rect(cx, start_y, card_w, 1.0, "F")
            
            # Değer
            self.set_xy(cx + 1, start_y + 1.5)
            self.set_font("DejaVu", "B", 10)
            self.set_text_color(*color)
            self.cell(card_w - 2, 4.8, str(val), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Etiket
            self.set_x(cx + 1)
            self.set_font("DejaVu", "B", 6.8)
            self.set_text_color(*SLATE_DARK)
            self.cell(card_w - 2, 3.2, label, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Not
            if note:
                self.set_x(cx + 1)
                self.set_font("DejaVu", "", 6.2)
                self.set_text_color(*SLATE_MED)
                self.cell(card_w - 2, 3.2, note, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
        self.set_y(start_y + card_h + 2.5)

    def table(self, headers, rows, widths=None, aligns=None):
        n_cols = len(headers)
        if not widths:
            widths = [178 / n_cols] * n_cols
        if not aligns:
            aligns = ["L"] * n_cols
            
        self.set_fill_color(*NAVY)
        self.set_font("DejaVu", "B", 7.2)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(*BORDER_COLOR)
        self.set_line_width(0.2)
        
        for i, h in enumerate(headers):
            self.cell(widths[i], 5.2, h, border=1, align=aligns[i], fill=True)
        self.ln(5.2)
        
        self.set_font("DejaVu", "", 6.8)
        for r_idx, row in enumerate(rows):
            bg = (255, 255, 255) if r_idx % 2 == 0 else BG_LIGHT
            self.set_fill_color(*bg)
            self.set_text_color(*SLATE_DARK)
            for i, val in enumerate(row):
                self.cell(widths[i], 4.6, str(val), border=1, align=aligns[i], fill=True)
            self.ln(4.6)
            
        self.ln(2.0)

    def figure(self, img_path, caption, max_h=55, max_w=165):
        if not os.path.exists(img_path):
            return
            
        self.fig_counter += 1
        cur_y = self.get_y()
        img_x = 16 + (178 - max_w) / 2
        
        with Image.open(img_path) as im:
            iw, ih = im.size
            rendered_h = (max_w / iw) * ih
            if rendered_h > max_h:
                rendered_h = max_h
                rendered_w = (max_h / ih) * iw
                img_x = 16 + (178 - rendered_w) / 2
            else:
                rendered_w = max_w
                
        self.set_draw_color(*BORDER_COLOR)
        self.set_line_width(0.3)
        self.image(img_path, x=img_x, y=cur_y, w=rendered_w, h=rendered_h)
        
        self.set_y(cur_y + rendered_h + 1.5)
        self.set_font("DejaVu", "I", 7.0)
        self.set_text_color(*SLATE_MED)
        cap_text = f"Şekil {self.fig_counter} · {caption}"
        self.multi_cell(0, 3.5, cap_text, align="C")
        self.ln(2.0)
