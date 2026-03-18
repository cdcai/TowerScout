// Event Listener Manager Module
// Prevents event listener memory leaks by tracking and managing all listeners
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Event Listener Management - Prevents event listener leaks
  class EventListenerManager {
    constructor() {
      this.listeners = new Map();
      console.log('🔧 EventListenerManager initialized');
    }

    addEventListener(element, event, callback, options = {}) {
      if (!element) {
        console.warn('⚠️ Cannot add event listener to null element');
        return null;
      }

      const wrappedCallback = (...args) => {
        try {
          callback(...args);
        } catch (error) {
          console.error('Event listener error:', error);
        }
      };

      element.addEventListener(event, wrappedCallback, options);

      // Store for cleanup
      const key = `${element.tagName || 'WINDOW'}-${event}`;
      if (!this.listeners.has(key)) {
        this.listeners.set(key, []);
      }
      this.listeners.get(key).push({
        element,
        event,
        callback: wrappedCallback,
        options
      });

      return wrappedCallback;
    }

    removeEventListener(element, event, callback) {
      if (!element) return false;

      element.removeEventListener(event, callback);

      // Remove from tracking
      const key = `${element.tagName || 'WINDOW'}-${event}`;
      const eventListeners = this.listeners.get(key);
      if (eventListeners) {
        const index = eventListeners.findIndex(l => l.callback === callback);
        if (index >= 0) {
          eventListeners.splice(index, 1);
          return true;
        }
      }
      return false;
    }

    removeAllListeners(element = null) {
      if (element) {
        // Remove listeners for specific element
        for (const [key, listeners] of this.listeners) {
          const filtered = listeners.filter(l => {
            if (l.element === element) {
              element.removeEventListener(l.event, l.callback, l.options);
              return false;
            }
            return true;
          });
          this.listeners.set(key, filtered);
        }
      } else {
        // Remove all listeners
        for (const [key, listeners] of this.listeners) {
          listeners.forEach(({ element, event, callback, options }) => {
            try {
              element.removeEventListener(event, callback, options);
            } catch (error) {
              console.warn('Failed to remove event listener:', error);
            }
          });
        }
        this.listeners.clear();
      }
    }

    getStats() {
      let totalListeners = 0;
      for (const listeners of this.listeners.values()) {
        totalListeners += listeners.length;
      }
      return {
        listenerTypes: this.listeners.size,
        totalListeners
      };
    }
  }

  // Create global instance
  window.eventManager = new EventListenerManager();

  console.log('✅ EventListenerManager module loaded');
})();
