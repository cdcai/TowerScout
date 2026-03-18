#!/bin/bash
# Extract GoogleMap class (lines 2517-3077)
echo "// TowerScout - GoogleMap Module" > providers/GoogleMap_extracted.js
echo "// Google Maps provider implementation" >> providers/GoogleMap_extracted.js
echo "// TASK-038 Stage 3: Extracted from monolithic towerscout.js" >> providers/GoogleMap_extracted.js
echo "" >> providers/GoogleMap_extracted.js
echo "(function() {" >> providers/GoogleMap_extracted.js
echo "  'use strict';" >> providers/GoogleMap_extracted.js
#echo "" >> providers/GoogleMap_extracted.js
sed -n '2517,3077p' towerscout.js >> providers/GoogleMap_extracted.js
echo "" >> providers/GoogleMap_extracted.js
echo "  // Export to window for global access (IIFE pattern)" >> providers/GoogleMap_extracted.js
echo "  window.GoogleMap = GoogleMap;" >> providers/GoogleMap_extracted.js
echo "" >> providers/GoogleMap_extracted.js
echo "  console.log('✅ GoogleMap module loaded');" >> providers/GoogleMap_extracted.js
echo "})();" >> providers/GoogleMap_extracted.js

# Extract AzureMap class (lines 1179-2510)
echo "// TowerScout - AzureMap Module" > providers/AzureMap_extracted.js
echo "// Azure Maps provider implementation" >> providers/AzureMap_extracted.js  
echo "// TASK-038 Stage 3: Extracted from monolithic towerscout.js" >> providers/AzureMap_extracted.js
echo "" >> providers/AzureMap_extracted.js
echo "(function() {" >> providers/AzureMap_extracted.js
echo "  'use strict';" >> providers/AzureMap_extracted.js
echo "" >> providers/AzureMap_extracted.js
sed -n '1179,2510p' towerscout.js >> providers/AzureMap_extracted.js
echo "" >> providers/AzureMap_extracted.js
echo "  // Export to window for global access (IIFE pattern)" >> providers/AzureMap_extracted.js
echo "  window.AzureMap = AzureMap;" >> providers/AzureMap_extracted.js
echo "" >> providers/AzureMap_extracted.js
echo "  console.log('✅ AzureMap module loaded');" >> providers/AzureMap_extracted.js
echo "})();" >> providers/AzureMap_extracted.js

# Extract TSMap base class (lines 1062-1169)
echo "// TowerScout - TSMap Base Class" > providers/TSMap_base.js
echo "// Abstract base class for all map providers" >> providers/TSMap_base.js
echo "// TASK-038 Stage 3: Extracted from monolithic towerscout.js" >> providers/TSMap_base.js
echo "" >> providers/TSMap_base.js
echo "(function() {" >> providers/TSMap_base.js
echo "  'use strict';" >> providers/TSMap_base.js
echo "" >> providers/TSMap_base.js
sed -n '1062,1169p' towerscout.js >> providers/TSMap_base.js
echo "" >> providers/TSMap_base.js
echo "  // Export to window for global access (IIFE pattern)" >> providers/TSMap_base.js
echo "  window.TSMap = TSMap;" >> providers/TSMap_base.js
echo "" >> providers/TSMap_base.js
echo "  console.log('✅ TSMap base class loaded');" >> providers/TSMap_base.js
echo "})();" >> providers/TSMap_base.js

echo "Extraction complete!"
