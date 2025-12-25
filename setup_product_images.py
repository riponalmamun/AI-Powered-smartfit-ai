"""
Setup Product Images - Creates placeholder images for all products
Run this once to generate demo images for virtual try-on
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(text, category, width=400, height=600, bg_color=(255, 255, 255)):
    """Create a simple placeholder image with product info"""
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add border
    border_color = (200, 200, 200)
    draw.rectangle([(10, 10), (width-10, height-10)], outline=border_color, width=3)
    
    # Add category-specific color accent
    category_colors = {
        'tshirt': (100, 149, 237),  # Cornflower blue
        'shirt': (70, 130, 180),     # Steel blue
        'dress': (219, 112, 147),    # Pale violet red
        'jeans': (65, 105, 225),     # Royal blue
        'hoodie': (128, 128, 128),   # Gray
        'jacket': (47, 79, 79),      # Dark slate gray
        'ethnic': (255, 215, 0),     # Gold
        'saree': (255, 105, 180),    # Hot pink
        'kurta': (255, 140, 0)       # Dark orange
    }
    
    accent_color = category_colors.get(category.lower(), (150, 150, 150))
    draw.rectangle([(20, 20), (width-20, 100)], fill=accent_color)
    
    # Add text
    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw product category
    text_bbox = draw.textbbox((0, 0), category.upper(), font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, 40), category.upper(), fill=(255, 255, 255), font=font_large)
    
    # Draw product name
    lines = text.split('\n')
    y_position = 150
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, y_position), line, fill=(80, 80, 80), font=font_small)
        y_position += 40
    
    # Add "Demo Image" watermark
    watermark = "DEMO PRODUCT"
    text_bbox = draw.textbbox((0, 0), watermark, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, height - 80), watermark, fill=(200, 200, 200), font=font_small)
    
    return img

def setup_product_images():
    """Read products.json and create all necessary images"""
    
    # Read products.json
    products_json_path = Path("products.json")
    if not products_json_path.exists():
        print("❌ Error: products.json not found!")
        return
    
    with open(products_json_path, 'r') as f:
        data = json.load(f)
        products = data.get('products', [])
    
    print(f"📦 Found {len(products)} products in products.json")
    print("🎨 Creating placeholder images...\n")
    
    created_count = 0
    skipped_count = 0
    
    for product in products:
        image_path = product.get('image_path', '')
        if not image_path:
            continue
        
        # Create full path
        full_path = Path(image_path)
        
        # Check if already exists
        if full_path.exists():
            print(f"⏭️  Skipped: {image_path} (already exists)")
            skipped_count += 1
            continue
        
        # Create directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate placeholder image
        product_name = product.get('name', 'Product')
        category = product.get('category', 'item')
        
        # Create image text
        image_text = f"{product_name}\n{product.get('style', '').title()}"
        
        # Generate image
        img = create_placeholder_image(image_text, category)
        
        # Save image
        img.save(full_path)
        print(f"✅ Created: {image_path}")
        created_count += 1
    
    print(f"\n🎉 Done!")
    print(f"   Created: {created_count} images")
    print(f"   Skipped: {skipped_count} images")
    print(f"\n✨ You can now use virtual try-on!")

if __name__ == "__main__":
    print("=" * 60)
    print("🖼️  SmartFit AI - Product Images Setup")
    print("=" * 60)
    print()
    
    setup_product_images()