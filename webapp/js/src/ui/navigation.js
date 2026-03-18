/**
 * STAGE 5 - UI & Final Integration
 * Module: navigation.js
 * Purpose: UI navigation controls and dialogs
 * 
 * Functions:
 * - about(aboutTotal): Display/dismiss About TowerScout splash screen with fade animation
 * - aboutTimerFunc(aboutTotal): Timer callback for about animation
 * - aboutOpacity(secs, total): Calculate fade opacity curve
 * - addClickDismissHandler(): Enable click-to-dismiss for about screen
 * - removeClickDismissHandler(): Clean up event listeners
 * - handleAboutClick(e): Handle click events on about screen
 * 
 * Dependencies:
 * - managers/TimerManager.js (timerManager)
 * - managers/EventManager.js (eventManager)
 * 
 * Exposed to window: about
 */

(function () {
  'use strict';

  // ===== Module-level variables for about dialog animation =====
  let aboutOp = 0;
  let aboutInterval = 20;
  let aboutIncrement = 20;
  let aboutTimer = null;
  let aboutCurrentTotal = 0;
  let aboutSecs = 0;

  // ===== About Dialog Functions =====

  function about(aboutTotal) {
    if (typeof aboutTotal === "undefined") {
      aboutTotal = 6;
    }

    // CRITICAL FIX: Proper dismissal logic instead of acceleration
    if (aboutTotal === 0) {
      // Clear any existing timer
      if (aboutTimer !== null) {
        clearTimeout(aboutTimer);
        aboutTimer = null;
      }
      // Immediate dismissal
      let adiv = document.getElementById("about_div");
      if (adiv) {
        adiv.style.display = "none";
        removeClickDismissHandler();
      }
      return;
    }

    // Clear any existing timer before starting new one
    if (aboutTimer !== null) {
      clearTimeout(aboutTimer);
      aboutTimer = null;
    }

    aboutOp = 1;
    aboutSecs = 0;
    aboutIncrement = 20;
    aboutInterval = 20;
    aboutCurrentTotal = aboutTotal;

    // Add click-to-dismiss functionality
    addClickDismissHandler();

    aboutTimer = timerManager.setTimeout(aboutTimerFunc, aboutInterval, aboutTotal);

    // FAILSAFE: Force dismiss after 10 seconds if something goes wrong
    timerManager.setTimeout(() => {
      const adiv = document.getElementById("about_div");
      if (adiv && adiv.style.display !== "none") {
        console.warn('⚠️ About screen failsafe triggered - forcing dismissal');
        adiv.style.display = "none";
        removeClickDismissHandler();
        if (aboutTimer !== null) {
          clearTimeout(aboutTimer);
          aboutTimer = null;
        }
      }
    }, 10000);
  }

  function aboutTimerFunc(aboutTotal) {
    let adiv = document.getElementById("about_div");

    let op = aboutOpacity(aboutSecs, aboutTotal)
    //console.log(op, aboutSecs, aboutTotal)
    if (op <= 0 || aboutSecs >= aboutTotal) {
      adiv.style.display = "none";
      removeClickDismissHandler(); // Clean up event listeners
      aboutTimer = null;
      return;
    }

    adiv.style.display = "flex";
    adiv.style.opacity = op;
    aboutSecs += aboutIncrement / 1000;
    aboutTimer = timerManager.setTimeout(aboutTimerFunc, aboutInterval, aboutTotal);
  }

  function aboutOpacity(secs, total) {
    //return Math.max(0, (total + 1) / total * (1 + 1 / (secs - total)))
    return -1 / Math.pow(secs - (total + 1), 4) + 1;
  }

  // ENHANCEMENT: Click-to-dismiss functionality for about screen
  function addClickDismissHandler() {
    const aboutDiv = document.getElementById("about_div");
    if (aboutDiv && !aboutDiv.hasAttribute('data-click-handler')) {
      eventManager.addEventListener(aboutDiv, 'click', handleAboutClick);
      aboutDiv.setAttribute('data-click-handler', 'true');
      aboutDiv.style.cursor = 'pointer';
    }
  }

  function removeClickDismissHandler() {
    const aboutDiv = document.getElementById("about_div");
    if (aboutDiv && aboutDiv.hasAttribute('data-click-handler')) {
      eventManager.removeAllListeners(aboutDiv);
      aboutDiv.removeAttribute('data-click-handler');
      aboutDiv.style.cursor = 'default';
    }
  }

  function handleAboutClick(e) {
    // Only dismiss if clicking the background, not the content
    if (e.target.id === 'about_div') {
      about(0); // Trigger immediate dismissal
    }
  }

  // ===== Expose to window for inline HTML handlers =====
  window.about = about;

  console.log('✅ Navigation module loaded (about dialog)');

})();
