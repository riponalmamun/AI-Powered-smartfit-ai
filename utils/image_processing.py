import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class ImageProcessor:
    @staticmethod
    def validate_image(image_path):
        try:
            img = Image.open(image_path)
            img.verify()
            return True, "Valid image"
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    @staticmethod
    def resize_image(image, max_size=1920):
        height, width = image.shape[:2]
        
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    @staticmethod
    def load_image(image_path):
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    @staticmethod
    def save_image(image, output_path):
        cv2.imwrite(str(output_path), image)
        return output_path
    
    @staticmethod
    def remove_background(image, mask):
        if mask is None:
            return image
        
        mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        result = cv2.bitwise_and(image, mask_3channel)
        
        return result
    
    @staticmethod
    def blend_images(background, foreground, mask=None, alpha=0.8):
        if mask is not None:
            mask_normalized = mask.astype(float) / 255.0
            mask_3channel = np.stack([mask_normalized] * 3, axis=-1)
            
            blended = (foreground * mask_3channel * alpha + 
                      background * (1 - mask_3channel * alpha))
            return blended.astype(np.uint8)
        else:
            return cv2.addWeighted(background, 1-alpha, foreground, alpha, 0)
    
    @staticmethod
    def adjust_brightness_contrast(image, brightness=0, contrast=0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
        
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)
        
        return image
    
    @staticmethod
    def get_image_quality_score(image_path):
        try:
            image = cv2.imread(str(image_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var > 500:
                quality = "high"
                score = min(laplacian_var / 1000, 1.0)
            elif laplacian_var > 100:
                quality = "medium"
                score = laplacian_var / 500
            else:
                quality = "low"
                score = laplacian_var / 100
            
            return {
                'quality': quality,
                'score': float(score),
                'sharpness': float(laplacian_var)
            }
        except Exception as e:
            return {
                'quality': 'unknown',
                'score': 0.5,
                'error': str(e)
            }