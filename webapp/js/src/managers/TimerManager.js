// Timer Manager Module
// Prevents memory leaks from uncleaned timers and intervals
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Timer Management System - Prevents memory leaks from uncleaned timers
  class TimerManager {
    constructor() {
      this.timers = new Set();
      this.intervals = new Set();
      console.log('🔧 TimerManager initialized');
    }

    setTimeout(callback, delay, ...args) {
      const timer = setTimeout(() => {
        this.timers.delete(timer);
        callback(...args);
      }, delay);
      this.timers.add(timer);
      return timer;
    }

    setInterval(callback, delay, ...args) {
      const interval = setInterval(() => {
        callback(...args);
      }, delay);
      this.intervals.add(interval);
      return interval;
    }

    clearTimeout(timer) {
      if (this.timers.has(timer)) {
        this.timers.delete(timer);
        clearTimeout(timer);
        return true;
      }
      return false;
    }

    clearInterval(interval) {
      if (this.intervals.has(interval)) {
        this.intervals.delete(interval);
        clearInterval(interval);
        return true;
      }
      return false;
    }

    clearAll() {
      console.log(`🧹 Cleaning up ${this.timers.size} timers and ${this.intervals.size} intervals`);

      this.timers.forEach(timer => clearTimeout(timer));
      this.intervals.forEach(interval => clearInterval(interval));

      this.timers.clear();
      this.intervals.clear();
    }

    getStats() {
      return {
        activeTimers: this.timers.size,
        activeIntervals: this.intervals.size
      };
    }
  }

  // Create global instance
  window.timerManager = new TimerManager();

  console.log('✅ TimerManager module loaded');
})();
