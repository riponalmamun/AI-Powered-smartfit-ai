import cv2
import numpy as np
from pathlib import Path
import mediapipe as mp
from utils.image_processing import ImageProcessor
from utils.ai_models import PersonSegmenter

class VirtualTryOn:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            min_detection_confidence=0.5
        )
        self.segmenter = PersonSegmenter()
        self.image_processor = ImageProcessor()
    
    def process_tryon(self, user_image_path, product_image_path, output_path):
        try:
            user_image = self.image_processor.load_image(user_image_path)
            product_image = self.image_processor.load_image(product_image_path)
            
            user_image = self.image_processor.resize_image(user_image)
            
            segmentation = self.segmenter.segment(user_image_path)
            person_mask = segmentation.get('mask')
            
            pose_landmarks = self._detect_pose(user_image)
            
            if pose_landmarks:
                fitted_clothing = self._fit_clothing_to_body(
                    product_image, 
                    user_image, 
                    pose_landmarks
                )
            else:
                fitted_clothing = self._simple_resize_clothing(
                    product_image, 
                    user_image
                )
            
            result = self._blend_clothing(
                user_image, 
                fitted_clothing, 
                person_mask
            )
            
            result = self._post_process(result)
            
            self.image_processor.save_image(result, output_path)
            
            quality_score = self._calculate_quality_score(result)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'quality_score': quality_score,
                'processing_complete': True
            }
        
        except Exception as e:
            print(f"Virtual try-on error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'output_path': None
            }
    
    def _detect_pose(self, image):
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            if results.pose_landmarks:
                return results.pose_landmarks.landmark
            return None
        except Exception as e:
            print(f"Pose detection error: {str(e)}")
            return None
    
    def _fit_clothing_to_body(self, product_image, user_image, landmarks):
        height, width = user_image.shape[:2]
        
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        
        shoulder_width = int(abs(right_shoulder.x - left_shoulder.x) * width * 1.3)
        torso_height = int(abs(left_hip.y - left_shoulder.y) * height * 1.2)
        
        if shoulder_width < 50 or torso_height < 50:
            return self._simple_resize_clothing(product_image, user_image)
        
        fitted = cv2.resize(product_image, (shoulder_width, torso_height))
        
        shoulder_center_x = int((left_shoulder.x + right_shoulder.x) / 2 * width)
        shoulder_y = int(left_shoulder.y * height)
        
        result = np.zeros_like(user_image)
        
        y1 = max(0, shoulder_y - 20)
        y2 = min(height, y1 + fitted.shape[0])
        x1 = max(0, shoulder_center_x - fitted.shape[1] // 2)
        x2 = min(width, x1 + fitted.shape[1])
        
        fitted_crop = fitted[0:(y2-y1), 0:(x2-x1)]
        result[y1:y2, x1:x2] = fitted_crop
        
        return result
    
    def _simple_resize_clothing(self, product_image, user_image):
        height, width = user_image.shape[:2]
        
        target_width = int(width * 0.4)
        target_height = int(height * 0.5)
        
        clothing_resized = cv2.resize(
            product_image, 
            (target_width, target_height)
        )
        
        result = np.zeros_like(user_image)
        
        y_offset = int(height * 0.15)
        x_offset = int((width - target_width) / 2)
        
        result[y_offset:y_offset+target_height, 
               x_offset:x_offset+target_width] = clothing_resized
        
        return result
    
    def _blend_clothing(self, user_image, clothing, mask):
        """Fixed blending function to handle array dimensions correctly"""
        result = user_image.copy()
        
        # Create a mask for where clothing exists (any non-zero pixel)
        # Use grayscale conversion to get single channel
        clothing_gray = cv2.cvtColor(clothing, cv2.COLOR_BGR2GRAY)
        clothing_mask = (clothing_gray > 0).astype(np.uint8)
        
        # Convert to 3-channel mask for proper blending
        clothing_mask_3ch = cv2.merge([clothing_mask, clothing_mask, clothing_mask])
        
        # Blend only where clothing exists
        if np.any(clothing_mask):
            # Create blended version of the entire image
            blended = cv2.addWeighted(user_image, 0.3, clothing, 0.7, 0)
            
            # Apply blending only where clothing mask is present
            result = np.where(clothing_mask_3ch > 0, blended, user_image)
        
        return result.astype(np.uint8)
    
    def _post_process(self, image):
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        image = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return image
    
    def _calculate_quality_score(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        score = min(laplacian_var / 500, 1.0)
        return float(score)