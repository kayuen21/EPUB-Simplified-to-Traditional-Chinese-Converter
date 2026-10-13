import os
from PIL import Image, ImageDraw, ImageFont

def draw_arrow(draw, start_x, start_y, end_x, end_y, color, width=3, arrow_size=12):
    """Draws a crisp geometric arrow from (start_x, start_y) to (end_x, end_y)."""
    # Main line
    draw.line([start_x, start_y, end_x - arrow_size + 2, end_y], fill=color, width=width)
    # Triangle head
    draw.polygon([
        (end_x, end_y),
        (end_x - arrow_size, end_y - arrow_size // 2),
        (end_x - arrow_size, end_y + arrow_size // 2)
    ], fill=color)

def create_usage_illustration(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 2x supersampled canvas for ultra-crisp rendering
    scale = 2
    w, h = 1200 * scale, 560 * scale
    img = Image.new('RGB', (w, h), (248, 250, 252)) # Slate 50 background
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_bold_path = "C:/Windows/Fonts/msyhbd.ttc"
    font_reg_path = "C:/Windows/Fonts/msyh.ttc"
    
    title_font = ImageFont.truetype(font_bold_path, 34 * scale)
    subtitle_font = ImageFont.truetype(font_reg_path, 18 * scale)
    card_step_font = ImageFont.truetype(font_bold_path, 16 * scale)
    card_title_font = ImageFont.truetype(font_bold_path, 22 * scale)
    card_desc_font = ImageFont.truetype(font_reg_path, 16 * scale)
    card_badge_font = ImageFont.truetype(font_bold_path, 14 * scale)
    card_sub_font = ImageFont.truetype(font_reg_path, 14 * scale)
    
    # Palette
    c_primary = (15, 23, 42)       # Slate 900
    c_secondary = (100, 116, 139)  # Slate 500
    c_card_bg = (255, 255, 255)    # White
    c_card_border = (226, 232, 240)# Slate 200
    c_teal = (13, 148, 136)        # Teal 600
    c_teal_light = (240, 253, 250) # Teal 50
    c_amber = (217, 119, 6)        # Amber 600
    c_red = (220, 38, 38)
    c_green = (16, 185, 129)
    
    # Header
    draw.text((w // 2, 45 * scale), "EPUB 簡體轉繁體工具 — 使用教學示意圖", font=title_font, fill=c_primary, anchor="mm")
    draw.text((w // 2, 85 * scale), "只需簡單將 .epub 檔案拖放至 exe 圖示，自動於同目錄輸出繁體電子書", font=subtitle_font, fill=c_secondary, anchor="mm")
    
    # 3 Steps Cards layout
    card_w = 340 * scale
    card_h = 370 * scale
    gap = 40 * scale
    total_cards_w = 3 * card_w + 2 * gap
    start_x = (w - total_cards_w) // 2
    card_y = 135 * scale
    
    steps = [
        {
            "step": "步驟 01",
            "title": "拖曳 EPUB 檔案",
            "desc": "選取任一簡體 .epub 電子書\n按住滑鼠左鍵直接拖曳",
            "badge": "來源：簡體書籍",
            "badge_color": c_red,
            "icon_type": "drag"
        },
        {
            "step": "步驟 02",
            "title": "放置於 EXE 圖示",
            "desc": "拖放至 epub-to-traditional.exe\n自動喚起極速轉換核心",
            "badge": "轉換核心：OpenCC",
            "badge_color": c_teal,
            "icon_type": "exe"
        },
        {
            "step": "步驟 03",
            "title": "同目錄即時生成",
            "desc": "內文、目錄、引號全部繁體化\n排版無損，原路徑立即讀取",
            "badge": "完成：正統繁體",
            "badge_color": c_green,
            "icon_type": "result"
        }
    ]
    
    for i, s in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        cy = card_y
        
        # Card Background & Shadow
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16 * scale, fill=c_card_bg, outline=c_card_border, width=2 * scale)
        
        # Step Tag
        tag_bg = c_teal_light if i == 1 else (241, 245, 249)
        tag_color = c_teal if i == 1 else c_secondary
        draw.rounded_rectangle([cx + 20 * scale, cy + 20 * scale, cx + 95 * scale, cy + 46 * scale], radius=6 * scale, fill=tag_bg)
        draw.text((cx + 57 * scale, cy + 33 * scale), s["step"], font=card_step_font, fill=tag_color, anchor="mm")
        
        # Card Title
        draw.text((cx + 20 * scale, cy + 65 * scale), s["title"], font=card_title_font, fill=c_primary)
        
        # Inner graphic box
        gfx_y = cy + 110 * scale
        gfx_h = 135 * scale
        draw.rounded_rectangle([cx + 20 * scale, gfx_y, cx + card_w - 20 * scale, gfx_y + gfx_h], radius=12 * scale, fill=(248, 250, 252), outline=(226, 232, 240), width=1 * scale)
        
        bx = cx + card_w // 2
        by = gfx_y + gfx_h // 2 - 10 * scale
        
        if s["icon_type"] == "drag":
            # Book box
            draw.rounded_rectangle([bx - 65 * scale, by - 40 * scale, bx + 65 * scale, by + 40 * scale], radius=8 * scale, fill=(254, 242, 242), outline=(248, 113, 113), width=2 * scale)
            draw.text((bx, by - 12 * scale), "EPUB 檔案", font=card_badge_font, fill=c_red, anchor="mm")
            draw.text((bx, by + 12 * scale), "解忧杂货店.epub", font=card_sub_font, fill=c_secondary, anchor="mm")
            draw.text((bx, by + 48 * scale), "按住滑鼠拖曳 (Drag)", font=card_sub_font, fill=c_red, anchor="mm")
            
        elif s["icon_type"] == "exe":
            # EXE Box
            draw.rounded_rectangle([bx - 80 * scale, by - 40 * scale, bx + 80 * scale, by + 40 * scale], radius=8 * scale, fill=(240, 253, 250), outline=c_teal, width=2 * scale)
            draw.text((bx, by - 12 * scale), "綠色獨立程式", font=card_badge_font, fill=c_teal, anchor="mm")
            draw.text((bx, by + 12 * scale), "epub-to-traditional.exe", font=card_sub_font, fill=c_primary, anchor="mm")
            draw.text((bx, by + 48 * scale), "“” 轉 「」  |  ‘’ 轉 『』", font=card_badge_font, fill=c_amber, anchor="mm")
            
        elif s["icon_type"] == "result":
            # Finished EPUB box
            draw.rounded_rectangle([bx - 70 * scale, by - 40 * scale, bx + 70 * scale, by + 40 * scale], radius=8 * scale, fill=(236, 253, 245), outline=(52, 211, 153), width=2 * scale)
            draw.text((bx, by - 12 * scale), "繁體 EPUB 完成", font=card_badge_font, fill=(5, 150, 105), anchor="mm")
            draw.text((bx, by + 12 * scale), "解憂雜貨店.epub", font=card_sub_font, fill=c_primary, anchor="mm")
            draw.text((bx, by + 48 * scale), "已儲存於原書籍目錄", font=card_sub_font, fill=(5, 150, 105), anchor="mm")

        # Description text below graphics
        desc_lines = s["desc"].split("\n")
        draw.text((cx + 20 * scale, cy + 265 * scale), desc_lines[0], font=card_desc_font, fill=c_secondary)
        if len(desc_lines) > 1:
            draw.text((cx + 20 * scale, cy + 292 * scale), desc_lines[1], font=card_desc_font, fill=c_secondary)
            
        # Feature pill at bottom
        pill_y = cy + 325 * scale
        draw.rounded_rectangle([cx + 20 * scale, pill_y, cx + card_w - 20 * scale, pill_y + 28 * scale], radius=6 * scale, fill=(241, 245, 249))
        draw.text((cx + card_w // 2, pill_y + 14 * scale), s["badge"], font=card_sub_font, fill=s["badge_color"], anchor="mm")

        # Draw connecting geometric arrows between cards
        if i < 2:
            arr_start_x = cx + card_w + 6 * scale
            arr_end_x = cx + card_w + gap - 6 * scale
            arr_y = cy + card_h // 2
            draw_arrow(draw, arr_start_x, arr_y, arr_end_x, arr_y, color=(148, 163, 184), width=3 * scale, arrow_size=12 * scale)

    # Downsample with Lanczos for smooth antialiasing
    final_img = img.resize((1200, 560), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG", optimize=True)
    print(f"Refined illustration saved to {output_path}")

if __name__ == "__main__":
    create_usage_illustration("C:/Users/kevin/Desktop/epub-chinese-converter/assets/usage.png")
