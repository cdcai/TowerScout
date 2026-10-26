// STAGE 5: Imagery Utilities
// Image processing and HTML element creation
(function () {
  'use strict';

  /**
   * Create DOM element from HTML string
   * @param {string} htmlString - HTML markup
   * @returns {Element} First child element
   */
  function createElementFromHTML(htmlString) {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
  }

  // Expose to window for global access
  window.createElementFromHTML = createElementFromHTML;

  window.TowerScoutLogger.debug('✅ Imagery utilities loaded');
})();
