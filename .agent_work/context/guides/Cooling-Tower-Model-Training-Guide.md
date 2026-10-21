# Comprehensive Guide to Cooling Tower Detection Model Development and Validation

This guide is structured to help a developer gain a deep understanding of how the cooling tower detection model was created, trained, validated, and its internal mechanisms. By the end of this document, the developer should have a comprehensive grasp of the nuances involved in the model's development and performance.

---

## Table of Contents

1. [Background](#background)
2. [Objective](#objective)
3. [Data Collection and Preparation](#data-collection-and-preparation)
   - [Manually Annotated Images](#manually-annotated-images)
   - [Synthetic Data Generation](#synthetic-data-generation)
   - [Model-Assisted Labeling](#model-assisted-labeling)
4. [Model Architecture](#model-architecture)
   - [Two-Stage Framework](#two-stage-framework)
   - [Stage 1: Object Detection (YOLOv5)](#stage-1-object-detection-yolov5)
   - [Stage 2: Image Classification (EfficientNet-b5)](#stage-2-image-classification-efficientnet-b5)
5. [Training Details](#training-details)
6. [Evaluation Metrics](#evaluation-metrics)
   - [Sensitivity, PPV, and F1](#sensitivity-ppv-and-f1)
   - [False Positives and False Negatives](#false-positives-and-false-negatives)
7. [Validation Results](#validation-results)
8. [Performance and Speed Comparison](#performance-and-speed-comparison)
9. [Common Issues and Future Improvements](#common-issues-and-future-improvements)
10. [Appendix: Technical Specifications](#appendix-technical-specifications)

---

## Background

Legionnaires’ disease is a severe pneumonia caused by Legionella bacteria, with community outbreaks often linked to improperly maintained cooling towers. Cooling towers are often identifiable via aerial imagery, but manual searches are time and labor-intensive.

The aim of this project was to develop a deep learning model for automatically detecting aerially visible cooling towers, which could significantly accelerate investigations during outbreaks, improve source identification, and potentially save lives.

---

## Objective

The primary purpose of the project was to train a machine learning model to automatically:
- Detect cooling towers using aerial imagery.
- Achieve high sensitivity (recall) and positive predictive value (precision) for cooling tower identification.
- Substantially reduce the time required for outbreak investigations compared to manual searches.

---

## Data Collection and Preparation

### Manually Annotated Images

1. **Data Sources:**
   - Satellite images were extracted from Google Maps covering:
     - New York City (NY, USA)
     - Philadelphia (PA, USA)
   - Cooling tower registry data were obtained from the Philadelphia Department of Public Health and publicly available New York City records.
   - Annotation was performed manually by a team of experts.

2. **Annotations:**
   - Cooling towers were annotated with bounding boxes using aerial imagery.
   - Each visible cooling tower in the image tile was individually annotated, including instances where multiple towers existed on the same building.

---

### Synthetic Data Generation

To improve model performance, synthetic training data were generated:
- **Backgrounds:** Aerial imagery from cities without visible cooling towers (Atlanta, Chicago, Houston).
- **Cut-and-Paste Method:**
  - Cooling towers were extracted and pasted onto background images.
  - Gaussian blurring with a 10-pixel radius was used to blend edges for realism.
- **Synthetic Dataset:** Added 119 images with 1–3 cooling towers per image.

---

### Model-Assisted Labeling

1. After a preliminary training phase, the model predicted potential cooling towers in new images.
2. Predictions from the model were manually reviewed and corrected.
3. This iterative process added additional training data from cities like Seattle, Las Vegas, Baton Rouge, and Irvine.

---

## Model Architecture

### Two-Stage Framework

The model used a **two-stage architecture** to balance sensitivity and precision:
1. **Stage 1 (Object Detection):** Identified potential cooling towers and assigned a probability.
2. **Stage 2 (Image Classification):** Further classified objects identified as intermediate probabilities to refine predictions.

---

### Stage 1: Object Detection (YOLOv5)

- **Model:** YOLOv5 (You Only Look Once Version 5) is an open-source object detection framework.
- **Task:** Detect potential cooling towers and localize them with bounding boxes.
- **Probability Thresholds:** 
  - **Low (<0.25):** Rejected as not cooling towers.
  - **Intermediate (0.25–0.65):** Passed to Stage 2.
  - **High (≥0.65):** Automatically accepted as cooling towers.
  
---

### Stage 2: Image Classification (EfficientNet-b5)

- **Model:** EfficientNet-b5, a deep learning image classification model. 
- **Task:** Binary classification of objects identified in Stage 1 with intermediate probabilities as either *cooling towers* or *not cooling towers*.
- **Input:** Cropped objects from YOLOv5 predictions.
- **Output:** Refined predictions with increased positive predictive value.

---

## Training Details

1. **Transfer Learning:**  
   Models were pretrained on large datasets:
   - **YOLOv5:** Pretrained on COCO 2017 object detection dataset (200,000+ images, 80 categories).
   - **EfficientNet-b5:** Pretrained on ImageNet (3M+ images, thousands of categories).

2. **Final Training Dataset:**  
   - 2,051 images containing 7,292 annotated cooling towers.
   - Divided images and annotations into training, validation, and test splits.

3. **Frameworks and Tools Used:**  
   - **YOLOv5 Implementation:** PyTorch.  
   - **Training Hardware:** GPU-supported Google CoLab (Tesla V100-SXM2-16GB).

---

## Evaluation Metrics

### Sensitivity, PPV, and F1

- **Sensitivity (Recall):** Proportion of true cooling towers correctly identified by the model.
- **Positive Predictive Value (PPV, Precision):** Proportion of detected cooling towers that were true positives.
- **F1 Score:** Harmonic mean of sensitivity and PPV.

---

### False Positives and False Negatives

1. **False Positives:** Objects mistakenly classified as cooling towers (e.g., patio umbrellas, water towers, air conditioners).
2. **False Negatives:** Cooling towers missed by the model (often due to obscurities or atypical shapes).

---

## Validation Results

1. **Test Datasets:**  
   - Split into New York City, Philadelphia, Boston, and Athens.
   - Boston and Athens were unseen during training.

2. **Performance in Key Locations:**
   - **New York City and Philadelphia:** 
     - Sensitivity: 95.1%
     - PPV: 90.1%
   - **Boston:** 
     - Sensitivity: 91.6%
     - PPV: 80.8%
   - **Athens:** 
     - Sensitivity: 86.9%
     - PPV: 85.5%

3. **Efficiency Comparison:**  
   - Model: ~7.6 seconds to scan 0.26 square miles (45 blocks).
   - Epidemiologists: ~83 min (manual inspection).

---

## Performance and Speed Comparison

| Metric              | Model         | Manual (Epidemiologists)     |
|---------------------|---------------|------------------------------|
| Sensitivity         | 91.6–95.1%   | Higher manual variability    |
| PPV                 | ~90%         | High expert accuracy         |
| Time (45 blocks)    | 7.6 seconds  | 55–125 minutes (83.75 min avg) |

---

## Common Issues and Future Improvements

1. **False Positives:**
   - Common artifacts resembling cooling towers included:
     - Radial symmetry (e.g., umbrellas, architectural features).
     - Misidentified air conditioning units.
   - Solution: Enhance pre/post-processing or refine training data.

2. **False Negatives:**
   - Cooling towers partially obscured or atypically shaped.
   - Solution: Add data augmentation techniques for robustness.

3. **Expanded Registry Support:**
   - Collaboration with more cities to build larger datasets.

---

## Appendix: Technical Specifications

- **Tile Resolution:** 1280 × 1280 pixels.
- **Zoom Level:** Covers ~21 km² per tile.
- **Augmentation:** Synthetic cooling towers and Gaussian blending.
- **Software:** PyTorch, Google CoLab.
- **Hardware:** NVIDIA Tesla V100 GPU.

--- 

This guide should provide a detailed understanding of the model, allowing you to build upon or modify it for similar use cases. For further assistance or clarifications, consult the associated research team or documentation. 