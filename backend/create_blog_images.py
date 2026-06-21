import os
from PIL import Image, ImageDraw, ImageFont

def draw_gradient_linear(draw, start_color, end_color, width, height, direction='vertical'):
    for i in range(height if direction == 'vertical' else width):
        # Calculate interpolation factor
        t = i / (height if direction == 'vertical' else width)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
        
        if direction == 'vertical':
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, height)], fill=(r, g, b))

def load_font(font_names, size):
    # Try common macOS font paths
    paths = [
        "/System/Library/Fonts/Supplemental/",
        "/System/Library/Fonts/",
        "/Library/Fonts/"
    ]
    for font_name in font_names:
        for p in paths:
            full_path = os.path.join(p, font_name)
            if os.path.exists(full_path):
                try:
                    return ImageFont.truetype(full_path, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def create_skincare_image():
    width, height = 900, 500
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # 1. Background: Deep Forest Green to Black gradient
    start_color = (20, 50, 35)   # Deep Jade
    end_color = (8, 15, 12)      # Near Black
    draw_gradient_linear(draw, start_color, end_color, width, height, 'vertical')
    
    # 2. Gold Borders
    gold = (201, 169, 110)       # #C9A96E
    draw.rectangle([20, 20, width - 20, height - 20], outline=gold, width=2)
    draw.rectangle([25, 25, width - 25, height - 25], outline=gold, width=1)
    
    # Decorative corner marks
    draw.line([(40, 40), (100, 40)], fill=gold, width=2)
    draw.line([(40, 40), (40, 100)], fill=gold, width=2)
    draw.line([(width - 40, 40), (width - 100, 40)], fill=gold, width=2)
    draw.line([(width - 40, 40), (width - 40, 100)], fill=gold, width=2)
    draw.line([(40, height - 40), (100, height - 40)], fill=gold, width=2)
    draw.line([(40, height - 40), (40, height - 100)], fill=gold, width=2)
    draw.line([(width - 40, height - 40), (width - 100, height - 40)], fill=gold, width=2)
    draw.line([(width - 40, height - 40), (width - 40, height - 100)], fill=gold, width=2)

    # 3. Typography
    # Try Georgia, Times New Roman, Arial
    serif_font = load_font(["Georgia.ttf", "Times New Roman.ttf"], 24)
    title_font = load_font(["Georgia.ttf", "Times New Roman.ttf"], 44)
    subtitle_font = load_font(["Arial.ttf", "Helvetica.ttf"], 18)
    
    # Brand Header
    draw.text((width // 2, 80), "L U M I A   B E A U T Y", fill=gold, font=serif_font, anchor="mm")
    draw.text((width // 2, 115), "S K I N C A R E   J O U R N A L", fill=(245, 240, 235), font=subtitle_font, anchor="mm")
    
    # Divider line
    draw.line([(width // 2 - 80, 135), (width // 2 + 80, 135)], fill=gold, width=1)
    
    # Main Title
    draw.text((width // 2, 230), "THE OILY SKIN ROUTINE", fill=(255, 255, 255), font=title_font, anchor="mm")
    draw.text((width // 2, 285), "10 Golden Steps for Clear, Balanced & Radiant Skin", fill=(180, 190, 185), font=serif_font, anchor="mm")
    
    # Bottom Label
    draw.text((width // 2, 400), "EST. 2026", fill=gold, font=subtitle_font, anchor="mm")
    draw.text((width // 2, 425), "EXPERT ADVICE", fill=(245, 240, 235), font=subtitle_font, anchor="mm")
    
    dest_dir = "/Users/siavash/Project/Lumia-Beauty-online-shop/backend/generated_images"
    os.makedirs(dest_dir, exist_ok=True)
    img.save(os.path.join(dest_dir, "blog_skin_care.png"), "PNG")
    print("Created blog_skin_care.png successfully!")

def create_perfume_image():
    width, height = 900, 500
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # 1. Background: Warm amber sunset to deep ocean teal/black
    start_color = (235, 140, 80)   # Warm Sunset Orange/Amber
    end_color = (15, 30, 45)       # Deep Ocean Teal
    draw_gradient_linear(draw, start_color, end_color, width, height, 'vertical')
    
    # 2. Gold Borders
    gold = (232, 196, 123)       # Light Amber Gold
    draw.rectangle([20, 20, width - 20, height - 20], outline=gold, width=2)
    draw.rectangle([25, 25, width - 25, height - 25], outline=gold, width=1)
    
    # Decorative corner marks
    draw.line([(40, 40), (100, 40)], fill=gold, width=2)
    draw.line([(40, 40), (40, 100)], fill=gold, width=2)
    draw.line([(width - 40, 40), (width - 100, 40)], fill=gold, width=2)
    draw.line([(width - 40, 40), (width - 40, 100)], fill=gold, width=2)
    draw.line([(40, height - 40), (100, height - 40)], fill=gold, width=2)
    draw.line([(40, height - 40), (40, height - 100)], fill=gold, width=2)
    draw.line([(width - 40, height - 40), (width - 100, height - 40)], fill=gold, width=2)
    draw.line([(width - 40, height - 40), (width - 40, height - 100)], fill=gold, width=2)

    # 3. Typography
    serif_font = load_font(["Georgia.ttf", "Times New Roman.ttf"], 24)
    title_font = load_font(["Georgia.ttf", "Times New Roman.ttf"], 44)
    subtitle_font = load_font(["Arial.ttf", "Helvetica.ttf"], 18)
    
    # Brand Header
    draw.text((width // 2, 80), "L U M I A   B E A U T Y", fill=gold, font=serif_font, anchor="mm")
    draw.text((width // 2, 115), "L' A R T   D U   P A R F U M", fill=(245, 240, 235), font=subtitle_font, anchor="mm")
    
    # Divider line
    draw.line([(width // 2 - 80, 135), (width // 2 + 80, 135)], fill=gold, width=1)
    
    # Main Title
    draw.text((width // 2, 230), "THE SUMMER FRAGRANCE GUIDE", fill=(255, 255, 255), font=title_font, anchor="mm")
    draw.text((width // 2, 285), "How to Choose Fresh, Citrusy & Aquatic Scents", fill=(225, 230, 235), font=serif_font, anchor="mm")
    
    # Bottom Label
    draw.text((width // 2, 400), "EST. 2026", fill=gold, font=subtitle_font, anchor="mm")
    draw.text((width // 2, 425), "SEASONAL Curation", fill=(245, 240, 235), font=subtitle_font, anchor="mm")
    
    dest_dir = "/Users/siavash/Project/Lumia-Beauty-online-shop/backend/generated_images"
    os.makedirs(dest_dir, exist_ok=True)
    img.save(os.path.join(dest_dir, "blog_summer_perfume.png"), "PNG")
    print("Created blog_summer_perfume.png successfully!")

if __name__ == "__main__":
    create_skincare_image()
    create_perfume_image()
