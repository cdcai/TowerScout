TowerScout dataset export
========================

This archive contains full imagery tiles, selected annotations above the UI
primary/secondary confidence threshold, and contents.txt for TowerScout restore.
Training labels include selected detections outside the Find boundary because
the full tile is included. Find-mode export warns about selected hidden ML
annotations and lets you cancel to inspect them in Label mode (which resets
the slider; restore your desired threshold). KML uses selected above-threshold
results: stored run membership for ML in Find mode, all in Label mode, and
explicitly selected manual towers in either mode. It does not recompute from
the current map view or drawing. Unchecked
or below-threshold detections are omitted intentionally. Review every full image
before training: an image under empty/ is not a verified negative example.

train/images/ contains JPEG tiles; train/labels/ contains YOLO annotations:
  0 center_x center_y width height
Coordinates and dimensions are normalized to the image. Selected manual
annotations are included. Tile dimensions vary by provider/export settings.
contents.txt records tiles, detection/selection data and the metadata flag; it
is not a backup of configuration, model weights or all persistent volumes.

Rights and provenance
---------------------
The application license does not grant rights to provider imagery. Google Maps,
Azure Maps and other imagery remain subject to the applicable provider/account
terms and permissions. Confirm that download, retention, reuse, redistribution
and training are permitted for your source and purpose. An exported archive
alone establishes none of those permissions. See PROVIDER_TERMS.md in the source
or application package. Annotation provenance and applicable rights must be
assessed separately; this README does not automatically license annotations
under AGPL or Creative Commons. Retain source and contributor attribution.

Review/export support: https://github.com/cdcai/TowerScout/issues
Source and current guidance: https://github.com/cdcai/TowerScout
Do not include provider credentials or sensitive imagery in public issues.

Attribution
-----------
Please cite TowerScout and the following publication when using the project:
Wong KK, Segura T, Mein G, Lu J, Hannapel EJ, Kunz JM, Ritter T, Smith JC,
Todeschini A, Nugen F, Edens C. Automated cooling tower detection through deep
learning for Legionnaires' disease outbreak investigations: a model development
and validation study. Lancet Digit Health. 2024;6(7):e500-e506.
https://doi.org/10.1016/S2589-7500(24)00094-3

Restore compatibility
---------------------
Restore accepts the current three-part contents.txt schema and the receiving
cdcai writer's legacy format: contiguous ordered tile indices with exactly one
leading tile pseudo-result per tile, all lacking ids. Mixed/missing/ambiguous
ids are rejected. ZIP64 is unsupported. Limits: 1,000 members, 64 MiB per member,
512 MiB expanded total, and 8 MiB UTF-8 contents.txt. Unknown metadata fields
are discarded, annotation whitespace is normalized, and provider credential
query values are redacted. Failed restore retains the current review.
Every tile must reference a distinct existing image with nonconflicting label
and XML destinations. JPEG/PNG/TIFF signature/structure checks apply, with
50 MiB, 8,192-pixel edge and 16-million-pixel limits. Reserved metadata paths
cannot be tile outputs. These checks do not certify image/training quality.
Legacy .jpg files containing valid PNG/TIFF bytes are preserved and accepted;
validation checks their actual content format instead of requiring a rename.
Export matches selections by tile ID and detection index, so equal label text
does not include an unchecked annotation. An empty ML selection remains empty.
Historical root and empty/README.txt copies are ignored on restore after archive
path and expansion checks; export includes one current README. XML coordinates
and width/height use the actual image dimensions, including rectangular images
and archives whose older metadata flags were flipped. The stored legacy flag
is decoded on restore; it no longer alternates during new round trips.

The archive does not store original search polygons. Existing membership flags
remain available; a new manual tower after restore has unconfirmed membership
(stored as false with a warning), stays visible, and remains eligible for export
when selected and above threshold. Changing map drawings does not reclassify
existing detections. Repeated manual-addition duplication remains a known
limitation; repeated export/restore is not a lossless
backup mechanism.
