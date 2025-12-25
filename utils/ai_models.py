import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp
from config import settings

class GenderAgeDetector:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=0.5
        )
    
    def detect(self, image_path):
        try:
            analysis = DeepFace.analyze(
                img_path=str(image_path),
                actions=['gender', 'age'],
                enforce_detection=False
            )
            
            if isinstance(analysis, list):
                analysis = analysis[0]
            
            gender = analysis.get('dominant_gender', 'unknown')
            age = analysis.get('age', 25)
            gender_confidence = analysis.get('gender', {}).get(gender.capitalize(), 0) / 100
            
            age_group = self._classify_age_group(age)
            
            return {
                'gender': 'male' if gender.lower() == 'man' else 'female',
                'gender_confidence': float(gender_confidence),
                'age': int(age),
                'age_group': age_group,
                'success': True
            }
        except Exception as e:
            print(f"Gender/Age detection error: {str(e)}")
            return {
                'gender': 'male',
                'gender_confidence': 0.5,
                'age': 25,
                'age_group': 'young_adults',
                'success': False,
                'error': str(e)
            }
    
    def _classify_age_group(self, age):
        if age < 13:
            return 'kids'
        elif age < 20:
            return 'teens'
        elif age < 36:
            return 'young_adults'
        else:
            return 'adults'

class BodyTypeDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            min_detection_confidence=0.5
        )
    
    def detect(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width = image.shape[:2]
            
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return self._default_response()
            
            landmarks = results.pose_landmarks.landmark
            
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            shoulder_width = abs(right_shoulder.x - left_shoulder.x) * width
            hip_width = abs(right_hip.x - left_hip.x) * width
            
            ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
            
            if ratio > 1.25:
                body_type = 'athletic'
            elif ratio < 1.05:
                body_type = 'plus_size'
            elif ratio < 1.15:
                body_type = 'average'
            else:
                body_type = 'slim'
            
            return {
                'body_type': body_type,
                'body_measurements': {
                    'shoulder_width': float(shoulder_width),
                    'hip_width': float(hip_width),
                    'ratio': float(ratio),
                    'height_estimate': int(height * 0.15)
                },
                'pose_quality': 'good',
                'success': True
            }
        except Exception as e:
            print(f"Body type detection error: {str(e)}")
            return self._default_response(error=str(e))
    
    def _default_response(self, error=None):
        return {
            'body_type': 'average',
            'body_measurements': {
                'shoulder_width': 45.0,
                'hip_width': 40.0,
                'ratio': 1.12,
                'height_estimate': 170
            },
            'pose_quality': 'unknown',
            'success': False,
            'error': error
        }

class PersonSegmenter:
    def __init__(self):
        self.mp_selfie = mp.solutions.selfie_segmentation
        self.segmenter = self.mp_selfie.SelfieSegmentation(model_selection=1)
    
    def segment(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.segmenter.process(image_rgb)
            mask = results.segmentation_mask
            
            mask_binary = (mask > 0.5).astype(np.uint8) * 255
            
            return {
                'mask': mask_binary,
                'original_image': image,
                'success': True
            }
        except Exception as e:
            print(f"Segmentation error: {str(e)}")
            return {
                'mask': None,
                'original_image': None,
                'success': False,
                'error': str(e)
            }