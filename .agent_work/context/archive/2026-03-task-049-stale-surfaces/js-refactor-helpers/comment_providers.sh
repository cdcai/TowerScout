#!/bin/bash
# Create backup first
cp towerscout.js towerscout.js.stage3.bak

# Comment out initGoogleMap and initAzureMap (lines 966-1056)
sed -i '966 i\// STAGE 3: Provider initialization functions extracted to src/providers/providerInit.js\n/*' towerscout.js
sed -i '1059 a\*/' towerscout.js

# Comment out TSMap, AzureMap, GoogleMap classes (lines 1062-3077, now shifted by 2 lines)
sed -i '1064 i\// STAGE 3: TSMap base class extracted to src/providers/TSMap_base.js\n// STAGE 3: AzureMap class extracted to src/providers/AzureMap.js\n// STAGE 3: GoogleMap class extracted to src/providers/GoogleMap.js\n/*' towerscout.js
sed -i '3084 a\*/' towerscout.js

echo "Provider classes commented out successfully"
