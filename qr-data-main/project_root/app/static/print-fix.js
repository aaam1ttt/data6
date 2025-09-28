// Enhanced print functionality fix for input field responsiveness after print preview
(function() {
  'use strict';

  // Store references to all input fields and their states
  let inputElements = [];
  let textareaElements = [];
  let originalEventListeners = new Map();
  let focusState = {
    activeElement: null,
    selectionStart: 0,
    selectionEnd: 0,
    scrollPosition: 0
  };

  function storeInputReferences() {
    // Store all input and textarea elements
    inputElements = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], input:not([type]), input[type="email"], input[type="tel"]'));
    textareaElements = Array.from(document.querySelectorAll('textarea'));
    
    // Store current focus state
    const activeEl = document.activeElement;
    if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
      focusState = {
        activeElement: activeEl,
        selectionStart: activeEl.selectionStart || 0,
        selectionEnd: activeEl.selectionEnd || 0,
        scrollPosition: activeEl.scrollTop || 0
      };
    }
  }

  function restoreInputFunctionality() {
    // Use multiple restoration attempts with increasing delays for better browser compatibility
    const delays = [50, 150, 300, 500, 1000];
    
    delays.forEach(delay => {
      setTimeout(() => {
        restoreInputsWithDelay();
      }, delay);
    });
  }

  function restoreInputsWithDelay() {
    // Restore all input fields
    [...inputElements, ...textareaElements].forEach(input => {
      if (input && input.parentNode && input.offsetParent !== null) {
        try {
          // Multiple restoration techniques for better browser compatibility
          
          // 1. Remove and re-add to DOM (most reliable)
          const parent = input.parentNode;
          const nextSibling = input.nextSibling;
          const inputClone = input.cloneNode(true);
          
          // Copy all properties
          inputClone.value = input.value;
          inputClone.disabled = input.disabled;
          inputClone.readonly = input.readonly;
          
          // Copy event listeners if they exist
          const events = ['input', 'change', 'keyup', 'keydown', 'focus', 'blur', 'paste'];
          events.forEach(eventType => {
            if (input['on' + eventType]) {
              inputClone['on' + eventType] = input['on' + eventType];
            }
          });
          
          // Replace the element
          parent.insertBefore(inputClone, nextSibling);
          parent.removeChild(input);
          
          // Update our reference
          const index = inputElements.indexOf(input);
          if (index !== -1) {
            inputElements[index] = inputClone;
          } else {
            const textareaIndex = textareaElements.indexOf(input);
            if (textareaIndex !== -1) {
              textareaElements[textareaIndex] = inputClone;
            }
          }
          
        } catch (e) {
          // Fallback method if DOM manipulation fails
          try {
            // Force re-initialization of input element
            input.blur();
            input.style.pointerEvents = 'none';
            setTimeout(() => {
              input.style.pointerEvents = 'auto';
              input.focus();
              input.blur();
              
              // Force re-render
              const display = input.style.display;
              input.style.display = 'none';
              input.offsetHeight; // Trigger reflow
              input.style.display = display;
              
            }, 10);
          } catch (fallbackError) {
            console.warn('Failed to restore input functionality:', fallbackError);
          }
        }
      }
    });
    
    // Restore focus state
    if (focusState.activeElement && focusState.activeElement.offsetParent !== null) {
      setTimeout(() => {
        try {
          focusState.activeElement.focus();
          if (focusState.activeElement.setSelectionRange) {
            focusState.activeElement.setSelectionRange(focusState.selectionStart, focusState.selectionEnd);
          }
          focusState.activeElement.scrollTop = focusState.scrollPosition;
        } catch (e) {
          console.warn('Failed to restore focus state:', e);
        }
      }, 100);
    }
  }

  // Enhanced window focus detection for tab switching
  function handleTabFocus() {
    document.addEventListener('visibilitychange', function() {
      if (!document.hidden) {
        // Tab became visible again - likely returning from print preview
        setTimeout(() => {
          restoreInputFunctionality();
        }, 200);
      }
    });
    
    window.addEventListener('focus', function() {
      // Window gained focus - possibly returning from print dialog
      setTimeout(() => {
        restoreInputFunctionality();
      }, 300);
    });
    
    // Page show event (for back/forward navigation or tab switching)
    window.addEventListener('pageshow', function(event) {
      if (event.persisted || performance.navigation.type === 2) {
        setTimeout(() => {
          restoreInputFunctionality();
        }, 100);
      }
    });
  }

  function enhancePrintFunction(originalPrintFn) {
    return function(...args) {
      // Store input references before print
      storeInputReferences();
      
      // Call original print function
      const result = originalPrintFn.apply(this, args);
      
      // Restore input functionality after print
      setTimeout(() => {
        restoreInputFunctionality();
      }, 100);
      
      return result;
    };
  }

  // Override window.print to handle the restoration
  if (window.print) {
    const originalWindowPrint = window.print;
    window.print = enhancePrintFunction(originalWindowPrint);
  }

  // Listen for print-related events
  window.addEventListener('beforeprint', function() {
    storeInputReferences();
  });
  
  window.addEventListener('afterprint', function() {
    setTimeout(() => {
      restoreInputFunctionality();
    }, 200);
  });

  // Enhanced window.open override for print windows
  const originalOpenWindow = window.open;
  window.open = function(url, target, features) {
    // Store state before opening any new window
    storeInputReferences();
    
    const newWindow = originalOpenWindow.call(this, url, target, features);
    
    if (newWindow && target === '_blank') {
      // Monitor the print window
      const originalWrite = newWindow.document.write;
      newWindow.document.write = function(content) {
        const result = originalWrite.apply(this, arguments);
        
        // If content includes print functionality
        if (content.includes('window.print()') || content.includes('window.onload') || content.includes('print')) {
          // Set up multiple restoration triggers
          const restoreDelays = [300, 600, 1000, 1500, 2000];
          restoreDelays.forEach(delay => {
            setTimeout(() => {
              if (newWindow.closed) {
                restoreInputFunctionality();
              }
            }, delay);
          });
          
          // Monitor window close
          const checkClosed = setInterval(() => {
            if (newWindow.closed) {
              clearInterval(checkClosed);
              restoreInputFunctionality();
            }
          }, 100);
          
          // Clean up after 10 seconds
          setTimeout(() => {
            clearInterval(checkClosed);
          }, 10000);
        }
        
        return result;
      };
      
      // Monitor for window close via unload event
      try {
        newWindow.addEventListener('beforeunload', () => {
          setTimeout(() => {
            restoreInputFunctionality();
          }, 200);
        });
        
        newWindow.addEventListener('unload', () => {
          setTimeout(() => {
            restoreInputFunctionality();
          }, 300);
        });
      } catch (e) {
        // Cross-origin restrictions may prevent this
      }
    }
    
    return newWindow;
  };

  // Initialize focus management
  handleTabFocus();

  // Initialize on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', storeInputReferences);
  } else {
    storeInputReferences();
  }
  
  // Re-initialize when DOM changes (for dynamic content)
  if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
      let shouldUpdate = false;
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1) { // Element node
              if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA' || 
                  (node.querySelector && (node.querySelector('input') || node.querySelector('textarea')))) {
                shouldUpdate = true;
              }
            }
          });
        }
      });
      
      if (shouldUpdate) {
        setTimeout(storeInputReferences, 100);
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // Periodic maintenance (as a last resort)
  setInterval(() => {
    const inputs = document.querySelectorAll('input, textarea');
    let hasUnresponsive = false;
    
    inputs.forEach(input => {
      try {
        if (input.offsetParent !== null) {
          const canFocus = input.tabIndex !== -1 && !input.disabled && !input.readonly;
          if (canFocus) {
            // Quick responsiveness test
            const originalValue = input.value;
            input.focus();
            if (document.activeElement !== input) {
              hasUnresponsive = true;
            }
            input.blur();
          }
        }
      } catch (e) {
        hasUnresponsive = true;
      }
    });
    
    if (hasUnresponsive) {
      restoreInputFunctionality();
    }
  }, 5000); // Check every 5 seconds

})();