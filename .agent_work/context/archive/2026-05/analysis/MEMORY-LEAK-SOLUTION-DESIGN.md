# Memory Management Solution - Technical Design

**Created**: 2026-02-04  
**Status**: DESIGN PHASE  
**Related Task**: TASK-035

## Problem Statement

Browser memory accumulates during extended TowerScout sessions with provider switching, causing performance degradation. Root cause: map provider infrastructure (event listeners, drawing managers, search components) not cleaned up when switching between Google Maps and Azure Maps.

## Solution Architecture

### Cleanup Strategy Hierarchy

```
┌─────────────────────────────────────────────────┐
│         ProviderStateManager                     │
│  - Coordinates provider switching                │
│  - Triggers cleanup before switch                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│         TSMap Base Class                         │
│  - Abstract cleanup() method                     │
│  - Defines cleanup contract                      │
└─────────────────────────────────────────────────┘
                    ↓
        ┌──────────┴──────────┐
        ↓                      ↓
┌──────────────┐      ┌──────────────┐
│  GoogleMap   │      │  AzureMap    │
│  cleanup()   │      │  cleanup()   │
└──────────────┘      └──────────────┘
```

### Component-Level Cleanup Design

#### 1. Drawing Manager Cleanup

**Current State**:
```javascript
// Azure - Line ~1248
this.drawingManager = new atlas.drawing.DrawingManager(this.map, {...});

// Google - Line ~1947  
this.drawingManager = new google.maps.drawing.DrawingManager({...});
```

**Proposed Solution**:
```javascript
// Add to AzureMap class
cleanupDrawingManager() {
  if (this.drawingManager) {
    // Remove event listeners
    this.map.events.remove('drawingcomplete', this.drawingManager);
    
    // Clear drawn shapes
    const source = this.drawingManager.getSource();
    if (source) {
      source.clear();
    }
    
    // Dispose drawing manager
    this.drawingManager.dispose();
    this.drawingManager = null;
    
    console.log('✅ Azure DrawingManager cleaned up');
  }
}

// Add to GoogleMap class
cleanupDrawingManager() {
  if (this.drawingManager) {
    // Remove all event listeners
    google.maps.event.clearInstanceListeners(this.drawingManager);
    
    // Remove from map
    this.drawingManager.setMap(null);
    this.drawingManager = null;
    
    console.log('✅ Google DrawingManager cleaned up');
  }
}
```

#### 2. Map Event Listener Cleanup

**Current Issue**: Direct map event attachment bypasses EventListenerManager

**Proposed Solution**: Tracking system for map-specific listeners

```javascript
// Add to both AzureMap and GoogleMap base state
this.mapEventListeners = [];

// Wrapper for map event attachment (Azure)
addMapListener(eventType, handler) {
  this.map.events.add(eventType, handler);
  this.mapEventListeners.push({ eventType, handler });
}

// Wrapper for map event attachment (Google)
addMapListener(eventType, handler) {
  const listener = google.maps.event.addListener(this.map, eventType, handler);
  this.mapEventListeners.push({ eventType, handler, listener });
}

// Cleanup method (Azure)
cleanupMapListeners() {
  for (const { eventType, handler } of this.mapEventListeners) {
    this.map.events.remove(eventType, handler);
  }
  this.mapEventListeners = [];
  console.log('✅ Azure map listeners cleaned up');
}

// Cleanup method (Google)
cleanupMapListeners() {
  for (const { listener } of this.mapEventListeners) {
    google.maps.event.removeListener(listener);
  }
  this.mapEventListeners = [];
  console.log('✅ Google map listeners cleaned up');
}
```

#### 3. Search Infrastructure Cleanup

**Azure Search Cleanup**:
```javascript
cleanupSearch() {
  // Remove search result markers and boundaries
  if (this.searchDataSource) {
    this.searchDataSource.clear();
    
    // Remove layers that reference this data source
    const layers = this.map.layers.getLayers();
    layers.forEach(layer => {
      const layerId = layer.getId();
      if (layerId && (
        layerId.includes('search') || 
        layerId.includes('boundary') ||
        layer.getSource() === this.searchDataSource
      )) {
        this.map.layers.remove(layer);
      }
    });
    
    // Remove data source
    this.map.sources.remove(this.searchDataSource);
    this.searchDataSource = null;
  }
  
  // Clear SearchURL
  this.searchURL = null;
  this.searchInitialized = false;
  
  console.log('✅ Azure search infrastructure cleaned up');
}
```

**Google Search Cleanup**:
```javascript
cleanupSearch() {
  // Remove SearchBox listeners
  if (this.searchBox) {
    google.maps.event.clearInstanceListeners(this.searchBox);
    this.searchBox = null;
  }
  
  // Clear places cache
  this.places = null;
  
  console.log('✅ Google search infrastructure cleaned up');
}
```

#### 4. Boundary Cleanup Enhancement

**Current Azure Implementation**: Partial cleanup
```javascript
resetBoundaries() {
  if (this.searchDataSource) {
    this.searchDataSource.clear(); // Clears data but not layers
  }
  this.boundaries = [];
}
```

**Enhanced Azure Implementation**:
```javascript
resetBoundaries() {
  // Clear boundary objects from data source
  if (this.searchDataSource) {
    const features = this.searchDataSource.getShapes();
    features.forEach(feature => {
      if (feature.properties && feature.properties.type === 'boundary') {
        this.searchDataSource.remove(feature);
      }
    });
  }
  
  // Clear boundary tracking
  this.boundaries.forEach(b => {
    b.azureObject = null; // Release reference
  });
  this.boundaries = [];
  
  console.log('✅ Azure boundaries cleaned up');
}
```

**Google Implementation**: Already correct, keep as-is
```javascript
resetBoundaries() {
  for (let b of this.boundaries) {
    b.object.setMap(null);
    b.object = null;
  }
  this.boundaries = [];
}
```

#### 5. Master Cleanup Method

**Add to TSMap base class**:
```javascript
// Abstract cleanup method - must be implemented by subclasses
cleanup() {
  throw new Error("cleanup() must be implemented by subclass");
}
```

**Add to AzureMap**:
```javascript
cleanup() {
  console.log('🧹 Starting Azure Maps cleanup...');
  
  // 1. Cleanup drawing manager
  this.cleanupDrawingManager();
  
  // 2. Cleanup map event listeners
  this.cleanupMapListeners();
  
  // 3. Cleanup search infrastructure
  this.cleanupSearch();
  
  // 4. Reset boundaries (already calls proper cleanup)
  this.resetBoundaries();
  
  // 5. Clear drawn shapes
  this.clearShapes();
  
  console.log('✅ Azure Maps cleanup complete');
}
```

**Add to GoogleMap**:
```javascript
cleanup() {
  console.log('🧹 Starting Google Maps cleanup...');
  
  // 1. Cleanup drawing manager
  this.cleanupDrawingManager();
  
  // 2. Cleanup map event listeners
  this.cleanupMapListeners();
  
  // 3. Cleanup search infrastructure
  this.cleanupSearch();
  
  // 4. Reset boundaries (already correct)
  this.resetBoundaries();
  
  // 5. Clear drawn shapes
  this.clearShapes();
  
  console.log('✅ Google Maps cleanup complete');
}
```

### Integration with ProviderStateManager

**Modify `switchProvider()` method**:
```javascript
async switchProvider(targetProvider, mapInstance = null) {
  if (this.switchingInProgress) {
    // ... existing wait logic ...
  }

  console.log(`🔄 Switching provider from ${this.currentProvider} to ${targetProvider}`);
  this.switchingInProgress = true;

  const rollbackState = {
    provider: this.currentProvider,
    map: this.currentMap
  };

  try {
    // ⭐ NEW: Cleanup previous provider BEFORE switching
    if (this.currentMap && typeof this.currentMap.cleanup === 'function') {
      console.log(`🧹 Cleaning up ${this.currentProvider} before switch...`);
      this.currentMap.cleanup();
    }

    // ... existing validation and switching logic ...
    
    // Atomic state update
    this.currentProvider = targetProvider;
    this.currentMap = availableMap;

    console.log(`✅ Provider switched: ${rollbackState.provider} → ${targetProvider}`);
    return true;

  } catch (error) {
    console.error('❌ Provider switch failed:', error);
    
    // Rollback (no cleanup needed since we cleaned up before switch)
    if (rollbackState.provider && rollbackState.map) {
      console.log(`🔄 Rolling back to ${rollbackState.provider}`);
      this.currentProvider = rollbackState.provider;
      this.currentMap = rollbackState.map;
    }

    TowerScoutErrorHandler.handleProviderError(targetProvider, error, 'Provider Switch');
    throw error;
  } finally {
    this.switchingInProgress = false;
  }
}
```

## Implementation Plan

### Phase 1: Base Infrastructure (30 minutes)
1. Add `cleanup()` abstract method to TSMap base class
2. Add `mapEventListeners` tracking array to both map classes
3. Create listener wrapper methods (`addMapListener`)

### Phase 2: Component Cleanup Methods (1 hour)
4. Implement `cleanupDrawingManager()` for both providers
5. Implement `cleanupMapListeners()` for both providers
6. Implement `cleanupSearch()` for both providers
7. Enhance `resetBoundaries()` for Azure Maps

### Phase 3: Master Cleanup Integration (30 minutes)
8. Implement `cleanup()` method for AzureMap
9. Implement `cleanup()` method for GoogleMap
10. Integrate cleanup call into `ProviderStateManager.switchProvider()`

### Phase 4: Validation & Testing (1 hour)
11. Test provider switching (Google ↔ Azure multiple times)
12. Monitor browser memory usage using DevTools
13. Verify no console errors related to disposed objects
14. Test extended session (>30 minutes with multiple switches)

## Success Metrics

### Memory Stability
- **Before**: Memory increases ~50-100MB per provider switch
- **Target**: Memory increase <10MB per switch (stable baseline)
- **Measurement**: Chrome DevTools Memory Profiler

### Performance
- **Before**: Provider switching takes 1-2 seconds after multiple switches
- **Target**: Provider switching remains <500ms consistently
- **Measurement**: `console.time()` around provider switch operations

### Stability
- **Before**: Console errors after 5-10 provider switches
- **Target**: Zero errors after 50+ switches
- **Measurement**: Browser console monitoring

## Testing Strategy

### Manual Testing Checklist
- [ ] Switch Google → Azure 10 times
- [ ] Switch Azure → Google 10 times
- [ ] Draw boundaries, switch provider, verify cleanup
- [ ] Search locations, switch provider, verify cleanup
- [ ] Run detection, switch provider, verify markers cleared
- [ ] Extended session test: 30 minutes of normal usage with switches
- [ ] Memory profiler: Heap snapshot before/after 20 switches

### Automated Testing (Future Enhancement)
- Unit tests for individual cleanup methods
- Integration tests for provider switching workflow
- Memory leak detection via Puppeteer

## Risks & Mitigations

### Risk 1: Breaking Existing Functionality
**Mitigation**: Implement cleanup methods incrementally, test each component

### Risk 2: Azure Maps Dispose Method Not Available
**Mitigation**: Check for method existence, use manual cleanup fallback

### Risk 3: Race Conditions During Cleanup
**Mitigation**: Leverage existing `switchingInProgress` flag in ProviderStateManager

### Risk 4: Third-Party Libraries Don't Release Resources
**Mitigation**: Set references to `null` to enable garbage collection even if libraries don't cleanup

## Migration & Rollback

### Backward Compatibility
- New cleanup methods are additive (no breaking changes)
- Existing code continues to work during incremental implementation
- Cleanup methods are defensive (check for null/undefined)

### Rollback Strategy
If cleanup causes issues:
1. Comment out cleanup call in `switchProvider()` 
2. Original behavior preserved (memory leaks but functional)
3. Individual cleanup methods can be disabled independently

## Future Enhancements

### Phase 2 Features (Post-TASK-035)
1. **Automated Memory Monitoring**: Dashboard showing current memory usage
2. **Cleanup Events**: Emit cleanup events for external monitoring
3. **Garbage Collection Hints**: Explicit `gc()` calls after cleanup (dev mode)
4. **Memory Budget Warnings**: Alert user if memory exceeds threshold

### Phase 3 Features
1. **Provider Instance Pool**: Reuse provider instances instead of full cleanup
2. **Lazy Resource Loading**: Load search/drawing tools only when needed
3. **Memory Profiling Integration**: Built-in memory profiler for development

## References

- **Azure Maps Disposal**: https://docs.microsoft.com/en-us/azure/azure-maps/how-to-use-map-control
- **Google Maps Memory Management**: https://developers.google.com/maps/documentation/javascript/examples/event-simple
- **JavaScript Memory Leaks**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_Management
- **Chrome DevTools Memory Profiler**: https://developer.chrome.com/docs/devtools/memory-problems/
