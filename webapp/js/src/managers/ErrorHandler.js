// Error Handler Module
// Comprehensive error handling with graceful degradation
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Error Boundary System - Comprehensive error handling with graceful degradation
  class TowerScoutErrorHandler {
    static setupGlobalErrorHandling() {
      // Catch all unhandled JavaScript errors
      window.addEventListener('error', (e) => {
        console.error('🚨 Global JavaScript error:', e.error);
        this.handleCriticalError(e.error, 'JavaScript Runtime Error');
      });

      // Catch all unhandled promise rejections
      window.addEventListener('unhandledrejection', (e) => {
        console.error('🚨 Unhandled promise rejection:', e.reason);
        this.handleAsyncError(e.reason, 'Promise Rejection');
        e.preventDefault(); // Prevent default browser error display
      });

      console.log('✅ Global error handling initialized');
    }

    static async handleProviderError(provider, error, context = 'Provider Operation') {
      console.error(`❌ ${provider} ${context} error:`, error);

      // Don't attempt automatic fallback from provider switching to prevent circular calls
      if (context === 'Provider Switch') {
        // For provider switch failures, just show error - let switchProvider handle rollback
        this.showUserNotification(`${provider} Maps unavailable. Using previous provider.`, 'warning');
        return false;
      }

      // For other provider errors (not during switching), attempt fallback
      const fallbackProvider = provider === 'azure' ? 'google' : 'azure';

      try {
        // Prevent premature failures during initial map loading
        if (window.providerManager.isProviderAvailable(fallbackProvider) && !window.providerManager.isInitializing) {
          console.log(`🔄 Attempting fallback to ${fallbackProvider}...`);
          await window.providerManager.switchProvider(fallbackProvider);
          this.showUserNotification(`Switched to ${fallbackProvider} Maps due to ${provider} error`, 'warning');
          return true;
        } else if (window.providerManager.isInitializing) {
          // During initial load, wait for proper initialization
          console.log('⏳ Maps still initializing, delaying error handling...');
          return true;
        } else {
          throw new Error(`No fallback provider available. ${fallbackProvider} not accessible.`);
        }
      } catch (fallbackError) {
        console.error('❌ Provider fallback failed:', fallbackError);
        // Only show fatal error if not during initial load
        if (!window.providerManager.isInitializing) {
          this.showFatalError(`All map providers failed. Please refresh the page.`);
        }
        return false;
      }
    }

    static handleNetworkError(error, operation = 'Network Operation') {
      console.error(`🌐 Network error during ${operation}:`, error);

      const isOffline = !navigator.onLine;
      const isTimeout = error.name === 'TimeoutError' || error.message.includes('timeout');
      const isRateLimit = error.message.includes('429') || error.message.includes('rate');

      if (isOffline) {
        this.showUserNotification('You appear to be offline. Please check your internet connection.', 'error');
      } else if (isTimeout) {
        this.showUserNotification('Request timed out. The server may be busy, please try again.', 'warning');
      } else if (isRateLimit) {
        this.showUserNotification('Rate limit exceeded. Please wait a moment before trying again.', 'warning');
      } else {
        this.showUserNotification(`Network error: ${error.message || 'Connection failed'}`, 'error');
      }
    }

    static handleCriticalError(error, source = 'Unknown') {
      console.error(`🚨 Critical error from ${source}:`, error);

      const errorMessage = error.message || error.toString() || 'Unknown error occurred';

      // Check if it's a provider-related error
      if (errorMessage.includes('Maps') || errorMessage.includes('provider')) {
        const provider = errorMessage.includes('Azure') ? 'azure' : 'google';
        this.handleProviderError(provider, error, source);
      } else {
        // Generic critical error handling
        this.showUserNotification(`Critical error: ${errorMessage}`, 'error');
      }
    }

    static handleAsyncError(reason, source = 'Async Operation') {
      console.error(`⚡ Async error from ${source}:`, reason);

      // Check if it's a network-related promise rejection
      if (reason && (reason.name === 'TypeError' && reason.message.includes('fetch')) ||
        (typeof reason === 'string' && reason.includes('network'))) {
        this.handleNetworkError(reason, source);
      } else {
        this.handleCriticalError(reason, source);
      }
    }

    static showUserNotification(message, type = 'info', timeout = 5000) {
      console.log(`📢 User notification [${type}]: ${message} (timeout: ${timeout}ms)`);

      // Clear any existing auto-hide timer
      if (this._notificationTimer) {
        window.timerManager.clearTimeout(this._notificationTimer);
        this._notificationTimer = null;
      }

      // Create or update notification element
      let notification = document.getElementById('error-notification');
      if (!notification) {
        notification = document.createElement('div');
        notification.id = 'error-notification';
        notification.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          max-width: 400px;
          padding: 12px 16px;
          border-radius: 4px;
          color: white;
          font-family: Arial, sans-serif;
          font-size: 14px;
          z-index: 10000;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: opacity 0.3s ease;
        `;
        document.body.appendChild(notification);
      }

      // Set color based on type
      const colors = {
        info: '#3498db',
        warning: '#f39c12',
        error: '#e74c3c',
        success: '#27ae60'
      };
      notification.style.backgroundColor = colors[type] || colors.info;
      notification.textContent = message;
      notification.style.opacity = '1';
      notification.style.display = 'block';

      // Auto-hide after timeout (if timeout > 0)
      if (timeout > 0) {
        this._notificationTimer = window.timerManager.setTimeout(() => {
          this.dismissNotification();
        }, timeout);
      }

      // Return notification ID for tracking
      return 'error-notification';
    }

    static dismissNotification() {
      console.log('📢 Dismissing notification');

      // Clear auto-hide timer if exists
      if (this._notificationTimer) {
        window.timerManager.clearTimeout(this._notificationTimer);
        this._notificationTimer = null;
      }

      const notification = document.getElementById('error-notification');
      if (notification) {
        notification.style.opacity = '0';
        window.timerManager.setTimeout(() => {
          if (notification && notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }
    }

    static showFatalError(message) {
      console.error('💀 Fatal error:', message);

      const fatalDiv = document.getElementById('fatal_div');
      if (fatalDiv) {
        const contentDiv = fatalDiv.querySelector('div');
        if (contentDiv) {
          contentDiv.innerHTML = `
            <h3>Application Error</h3>
            <p>${message}</p>
            <p>Please refresh the page to continue.</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px;">Refresh Page</button>
          `;
        }
        fatalDiv.style.display = 'flex';
      }
    }

    static wrapAsyncOperation(operation, operationName = 'Async Operation') {
      return async (...args) => {
        try {
          return await operation(...args);
        } catch (error) {
          this.handleAsyncError(error, operationName);
          throw error; // Re-throw to allow caller to handle if needed
        }
      };
    }

    static wrapNetworkCall(networkCall, operationName = 'Network Call') {
      return async (...args) => {
        try {
          return await networkCall(...args);
        } catch (error) {
          this.handleNetworkError(error, operationName);
          throw error; // Re-throw to allow caller to handle if needed
        }
      };
    }
  }

  // Expose globally
  window.TowerScoutErrorHandler = TowerScoutErrorHandler;

  console.log('✅ ErrorHandler module loaded');
})();
