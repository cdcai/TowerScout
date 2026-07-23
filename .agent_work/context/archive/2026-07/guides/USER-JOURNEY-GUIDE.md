# **Towerscout Development Guide: User Journey and System Functionality**

## **Executive Summary** 
This guide outlines the technical workflow and user interactions for **Towerscout**, an application designed to identify cooling towers from satellite imagery using machine learning.

**Important Note:**
The technical workflow and user interactions are based on the **legacy** Towerscout application. These workflows and user interactions **Must** be present in the improved version, in addition to the new features planned for future development (i.e., Setup Wizard, and settings panel). 

---
## **Technical Workflow and User Interactions (6 Stages)** 
 
### **Stage 1: Environment Setup and Provider Selection**
Before initiating a search, the user must configure the map backend to ensure the highest quality data for the target area.
 
*   **User Action:** Toggle the user interface between **Google and Azure** map providers.
*   **Expected Result:** The system displays satellite imagery from the selected provider. Users compare the two to determine which offers better imagery for the specific city of interest.
*   **Developer Note:** Once a provider is selected, that backend must be used by the machine learning model for all subsequent predictions in that session.
 
---
 
### **Stage 2: Area of Interest (AOI) Definition**
Users define the geographic boundaries where the model will search for cooling towers.
 
*   **Available Actions:**
    *   **Basic Navigation:** Dragging and zooming to find an area.
    *   **Automated Outlining:** Search by **Address or City or Neighborhood** to have the system automatically outline the boundary on the map.
    *   **Zip Code Search:** Enter a zip code into the search bar.
    *   **Radius Search (Circle Tool):** Select a specific point on the map, define a radius, and select the **Circle tool**.
    *   **Polygon (Custom Shape) Tool:** Use the **Polygon tool** to draw a custom shape by selecting points that enclose the area.
    *   **Clear tool:** Use the **Clear tool** to remove custom drawn shapes or previously defined radius circles. 
*   **Expected Result:** The map reflects the defined search area. The polygon tool is specifically used to **omit irrelevant areas** (e.g., forests, bodies of water) to optimize processing time.
 
---
 
### **Stage 3: Search Execution and Processing**
Once the area is defined, the user initiates the machine learning analysis.
 
*   **User Action:** Click **"Estimate Tiles"** to understand the processing time.
*   **User Action:** Click **"Find Towers"** (also referred to as "Kick off search" or "fire off query").
*   **System Logic:** The system feeds satellite imagery into machine learning algorithms to detect towers.
*   **Expected Result:** For optimal performance, searches should be kept to **100 tiles or less** (roughly a half-mile radius), which typically completes in **30 seconds or less**. Results are returned in a "familiar format" showing identified towers and building addresses.
 
---
 
### **Stage 4: Results Review and Refinement (Browse Mode)**
Users interact with the returned data to ensure accuracy, which is critical during scenarios like Legionnaire's disease outbreaks.
 
*   **Available Actions:**
    *   **Review Detections:** Click a detected tower in the right-hand panel or its address.
    *   **Map Sync:** Clicking an address highlights the associated tower on the map.
    *   **Filter Results:** **Toggle confidence levels** returned by the model or switch between **"tile by tile"** and **"tower by tower"** review modes.
    *   **Remove False Positives:** Use the **checkbox** to deselect items improperly identified as towers.
    *   **Manual Addition:** Use the **Polygon tool** to highlight and manually add towers the model missed.
*   **Expected Result:** The right-hand panel displays the **address, confidence level, and capture date** (if available) for the selected detection. The user-refined list becomes the final dataset.
 
---
 
### **Stage 5: Label Mode (Model Training & Registry Building)**
This specialized mode is used to gather training data to improve the model or build comprehensive registries.
 
*   **User Action:** Toggle into **"Label Mode"**.
*   **System Behavior:** The system returns **all towers within relevant tiles**, even those outside the initial search boundary, because the model learns from full tiles.
*   **Action/Result:** Users click through tiles to verify results, using the polygon tool to label missed towers and deselecting any detections that are not actually towers.
 
---
 
### **Stage 6: Data Export**
The final stage of the workflow involves exporting the refined data for field use or 3D analysis.
 
*   **User Action:** Click **"Download Results"**.
*   **Expected Results/Outcomes:**
    *   **Excel/CSV Export:** Used for easy tracking of towers and recording which sites have been visited or sampled.
    *   **KML Export:** Used for **3D visualization** in external tools like Google Earth.

---
