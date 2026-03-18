# Decision Record 002: ML Model Protection Policy

**Date**: November 18, 2025  
**Status**: Approved  
**Decision Maker**: Project Stakeholder  

## Decision

Establish strict protection boundaries for TowerScout's machine learning components to preserve proven detection capabilities while allowing user experience and infrastructure improvements.

## Context

TowerScout has been successfully deployed in 12+ Legionnaires' disease outbreak investigations across 8 states, demonstrating proven ML detection capabilities. The improvement project aims to enhance user experience and infrastructure without compromising the core detection functionality that makes TowerScout valuable for public health applications.

## Protected Components

### Strictly Protected (No Changes Without Explicit Approval)
- **`Model/` directory**: All training notebooks, evaluation scripts, and model development code
- **Model weights**: `webapp/model_params/yolov5/newest.pt` and `webapp/model_params/EN/b5_unweighted_best.pt`
- **Core detection logic**: Essential algorithms in `ts_yolov5.py` and `ts_en.py`
- **Model architecture**: YOLOv5 and EfficientNet configurations

### Safe for Enhancement
- **Flask application**: `webapp/towerscout.py` routes and session management
- **User interface**: `templates/`, `css/`, `js/` files
- **Map providers**: `ts_maps.py`, `ts_gmaps.py`, `ts_bmaps.py` interfaces
- **Configuration and deployment**: Scripts, Docker files, documentation
- **Supporting utilities**: `ts_imgutil.py`, `ts_events.py`, `ts_zipcode.py` (with care)

## Options Evaluated

### Option A: Complete Hands-Off
**Pros**: Zero risk to ML functionality  
**Cons**: Prevents necessary infrastructure improvements, limits optimization opportunities

### Option B: Selective Protection (Selected)
**Pros**: Preserves proven ML capabilities while enabling infrastructure improvements  
**Cons**: Requires careful boundary management and approval processes

### Option C: Full Optimization Freedom
**Pros**: Maximum optimization potential  
**Cons**: High risk of breaking proven detection capabilities

## Rationale

Option B (selective protection) was chosen because:

1. **Proven Track Record**: TowerScout's ML detection capabilities have been validated in real-world public health scenarios. This proven effectiveness must be preserved.

2. **Risk Management**: The cost of breaking detection accuracy is extremely high given the public health applications. Conservative approach is warranted.

3. **Infrastructure Needs**: The application requires significant infrastructure improvements (security, UX, deployment) that don't require ML model changes.

4. **Future Flexibility**: Protection policy can be relaxed in future phases once infrastructure improvements are stable and validated.

5. **Clear Boundaries**: Well-defined protected areas reduce ambiguity and accidental modifications.

## Implementation Guidelines

### Development Workflow
1. **Pre-change Review**: Any change touching protected areas requires explicit approval
2. **Baseline Testing**: ML detection accuracy must be benchmarked before and after changes
3. **Validation Protocol**: All changes must pass detection accuracy validation
4. **Rollback Plan**: Immediate rollback procedures for any accuracy degradation

### Specific Restrictions
- **No torch.quantization**: Model optimization deferred until explicit approval
- **No model weight modifications**: Existing weights preserved exactly
- **No training pipeline changes**: Model development workflow unchanged
- **No core algorithm changes**: Detection logic in `ts_yolov5.py` and `ts_en.py` protected

### Monitoring and Validation
- **Accuracy Benchmarks**: Establish baseline accuracy metrics
- **Regression Testing**: Automated tests to detect ML pipeline changes
- **Performance Monitoring**: Track inference time and resource usage
- **Validation Dataset**: Maintain test dataset for accuracy verification

## Impact

**Development Constraints**:
- Slower optimization of ML inference pipeline
- More conservative approach to performance improvements
- Additional validation steps for changes near ML components
- Deferred CPU optimization features like quantization

**Benefits**:
- Preserved public health tool reliability
- Reduced risk of breaking proven functionality
- Clear development boundaries and guidelines
- Maintained user trust and adoption

**Future Considerations**:
- CPU optimization features can be revisited in Phase 5
- Model updates can be considered after infrastructure stabilization
- Performance optimization opportunities can be evaluated with baseline metrics

## Review

This policy will be reviewed after successful completion of infrastructure improvements:

**Phase 1 Review** (After Flask Core completion):
- Assess impact of protection policy on development velocity
- Validate effectiveness of boundary enforcement
- Review any near-miss incidents or ambiguous cases

**Phase 4 Review** (After all infrastructure improvements):
- Evaluate opportunities for ML pipeline optimization
- Consider relaxing restrictions for performance improvements
- Assess feasibility of CPU optimization features
- Review model update and enhancement possibilities

Scheduled reviews: Week 4 (Phase 1 complete) and Week 12 (full project complete)