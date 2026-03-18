TowerScout Dataset Export - README
================================================================================

This ZIP file contains cooling tower detection data exported from TowerScout
for machine learning training and analysis.

Dataset Contents:
--------------------------------------------------------------------------------

1. train/images/  - Satellite imagery tiles (640x640 pixels, JPEG format)
2. train/labels/  - YOLO format annotation files (.txt)
3. contents.txt   - Dataset manifest and metadata
4. README.txt     - This file

File Structure:
--------------------------------------------------------------------------------

Each image file has a corresponding label file with the same name:
  - train/images/tile_123.jpg
  - train/labels/tile_123.txt

Label Format (YOLO):
--------------------------------------------------------------------------------

Each line in a .txt label file represents one cooling tower detection:

  <class> <center_x> <center_y> <width> <height>

Where:
  - class: Object class (always 0 for cooling towers)
  - center_x, center_y: Center coordinates (normalized 0.0-1.0)
  - width, height: Bounding box dimensions (normalized 0.0-1.0)

Example:
  0 0.5123 0.4876 0.0625 0.0834

This represents a cooling tower at center (51.23%, 48.76%) of the image
with width 6.25% and height 8.34% of the image dimensions.

Detection Types:
--------------------------------------------------------------------------------

This dataset includes two types of detections:

1. ML Detections: Detected by YOLOv5 + EfficientNet models
   - Confidence scores range from 0.0 to 1.0
   - Only detections above your selected threshold are included

2. Manual Additions: Manually added by users during investigation
   - Marked with confidence = 1.0
   - Useful for correcting false negatives or adding known towers

Using This Dataset:
--------------------------------------------------------------------------------

For YOLOv5 Training:
--------------------

1. Extract this ZIP file to your training directory

2. Create a data.yaml file:
   
   path: /path/to/dataset
   train: train/images
   val: train/images  # Or create separate validation set
   
   names:
     0: cooling_tower

3. Train with YOLOv5:
   
   python train.py --img 640 --batch 16 --epochs 100 \
     --data data.yaml --weights yolov5s.pt

4. For best results:
   - Minimum 100-200 annotated images recommended
   - Include diverse imagery (different angles, weather, zoom levels)
   - Balance positive and negative examples

For Analysis/Review:
-------------------

1. Open images in any image viewer
2. Review label files to see bounding boxes
3. Use contents.txt to see original detection metadata

Dataset Metadata:
--------------------------------------------------------------------------------

See contents.txt for:
- Export timestamp
- Map provider used (Google Maps / Azure Maps)
- Confidence threshold applied
- Total number of detections (ML + Manual)
- Geographic coordinates for each tile

Quality Notes:
--------------------------------------------------------------------------------

- Manual additions are marked by investigators to correct false negatives
- Review confidence scores in contents.txt to assess quality
- Some tiles may have multiple detections per image
- Bounding boxes are approximate - actual cooling towers may vary

Citation:
--------------------------------------------------------------------------------

If using this data for research or publications, please cite:

Wong, KK, Segura T, Mein G, Lu J, Hannapel EJ, Kunz JM, Ritter T, Smith JC, 
Todeschini A, Nugen F, Edens C. Automated cooling tower detection through 
deep learning for Legionnaires' disease outbreak investigations: a model 
development and validation study. Lancet Digit Health. 2024;6(7):e500-e506.
doi.org/10.1016/S2589-7500(24)00094-3

Support:
--------------------------------------------------------------------------------

For questions or issues:
- GitHub: https://github.com/CDC-WDPB/TowerScout
- Documentation: See TowerScout repository README.md

License:
--------------------------------------------------------------------------------

This dataset is provided under CC-BY-NC-SA-4.0 license.
Commercial use requires permission.

================================================================================
TowerScout - Automated Cooling Tower Detection for Legionnaires' Disease
Outbreak Investigations
================================================================================
