(function () {
  'use strict';

  const EPSILON = 1e-12;
  const AREA_EPSILON = 1e-12;

  function isFinitePoint(point) {
    return Array.isArray(point)
      && point.length === 2
      && Number.isFinite(point[0])
      && Number.isFinite(point[1]);
  }

  function almostEqual(a, b, epsilon = EPSILON) {
    return Math.abs(a - b) <= epsilon;
  }

  function samePoint(a, b, epsilon = EPSILON) {
    return almostEqual(a[0], b[0], epsilon) && almostEqual(a[1], b[1], epsilon);
  }

  function normalizePoints(points) {
    if (!Array.isArray(points)) {
      return [];
    }

    const normalized = [];
    for (const point of points) {
      if (!isFinitePoint(point)) {
        continue;
      }

      const normalizedPoint = [Number(point[0]), Number(point[1])];
      if (normalized.length === 0 || !samePoint(normalizedPoint, normalized[normalized.length - 1])) {
        normalized.push(normalizedPoint);
      }
    }

    if (normalized.length > 1 && samePoint(normalized[0], normalized[normalized.length - 1])) {
      normalized.pop();
    }

    return normalized;
  }

  function closeRing(points) {
    if (points.length === 0) {
      return [];
    }

    const closed = points.map((point) => [point[0], point[1]]);
    if (!samePoint(closed[0], closed[closed.length - 1])) {
      closed.push([closed[0][0], closed[0][1]]);
    }

    return closed;
  }

  function polygonArea(points) {
    let area = 0;
    for (let i = 0; i < points.length - 1; i++) {
      area += points[i][0] * points[i + 1][1] - points[i + 1][0] * points[i][1];
    }

    return Math.abs(area) / 2;
  }

  function orientation(a, b, c) {
    const cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
    if (almostEqual(cross, 0)) {
      return 0;
    }

    return cross > 0 ? 1 : -1;
  }

  function onSegment(a, b, c) {
    return b[0] <= Math.max(a[0], c[0]) + EPSILON
      && b[0] >= Math.min(a[0], c[0]) - EPSILON
      && b[1] <= Math.max(a[1], c[1]) + EPSILON
      && b[1] >= Math.min(a[1], c[1]) - EPSILON;
  }

  function segmentsIntersect(a1, a2, b1, b2) {
    const o1 = orientation(a1, a2, b1);
    const o2 = orientation(a1, a2, b2);
    const o3 = orientation(b1, b2, a1);
    const o4 = orientation(b1, b2, a2);

    if (o1 !== o2 && o3 !== o4) {
      return true;
    }

    if (o1 === 0 && onSegment(a1, b1, a2)) return true;
    if (o2 === 0 && onSegment(a1, b2, a2)) return true;
    if (o3 === 0 && onSegment(b1, a1, b2)) return true;
    if (o4 === 0 && onSegment(b1, a2, b2)) return true;

    return false;
  }

  function hasSelfIntersection(points) {
    const segmentCount = points.length - 1;
    for (let i = 0; i < segmentCount; i++) {
      const a1 = points[i];
      const a2 = points[i + 1];

      for (let j = i + 1; j < segmentCount; j++) {
        if (Math.abs(i - j) <= 1) {
          continue;
        }

        if (i === 0 && j === segmentCount - 1) {
          continue;
        }

        const b1 = points[j];
        const b2 = points[j + 1];
        if (segmentsIntersect(a1, a2, b1, b2)) {
          return true;
        }
      }
    }

    return false;
  }

  function validatePolygon(points) {
    const normalized = normalizePoints(points);
    if (normalized.length < 3) {
      return {
        valid: false,
        reason: 'too_few_points',
        points: normalized
      };
    }

    const closed = closeRing(normalized);

    if (hasSelfIntersection(closed)) {
      return {
        valid: false,
        reason: 'self_intersection',
        points: normalized
      };
    }

    if (polygonArea(closed) <= AREA_EPSILON) {
      return {
        valid: false,
        reason: 'zero_area',
        points: normalized
      };
    }

    return {
      valid: true,
      reason: null,
      points: normalized,
      closedPoints: closed
    };
  }

  function validatePolygonCollection(polygons) {
    if (!Array.isArray(polygons) || polygons.length === 0) {
      return {
        valid: true,
        polygons: []
      };
    }

    for (let i = 0; i < polygons.length; i++) {
      const validation = validatePolygon(polygons[i]);
      if (!validation.valid) {
        return {
          ...validation,
          polygonIndex: i
        };
      }
    }

    return {
      valid: true,
      polygons
    };
  }

  function getUserMessage(validation, label = 'custom shape', options = {}) {
    const prefix = `Invalid ${label}: `;
    const remediation = options.remediation || 'clear_then_redraw';

    function getRemediationText() {
      if (remediation === 'edit_or_redraw') {
        return 'Use Edit Geometry or redraw the shape.';
      }

      return 'Click Clear to remove it, then redraw a valid shape.';
    }

    switch (validation.reason) {
      case 'self_intersection':
        return `${prefix}polygon lines cannot cross. ${getRemediationText()}`;
      case 'too_few_points':
        return `${prefix}draw at least 3 distinct points to create an enclosed area.`;
      case 'zero_area':
        return `${prefix}the polygon must enclose a non-zero area. ${getRemediationText()}`;
      default:
        return `${prefix}the polygon is malformed. ${getRemediationText()}`;
    }
  }

  window.PolygonValidation = {
    validatePolygon,
    validatePolygonCollection,
    getUserMessage
  };

  window.TowerScoutLogger.debug('✅ Polygon validation utilities loaded');
})();
