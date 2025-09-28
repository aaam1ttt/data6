// Print functionality fix for input field responsiveness after print preview
(function() {
  'use strict';

  // Store references to all input fields for re-initialization
  let inputElements = [];
  let textareaElements = [];
  let originalEventListeners = new Map();

  function storeInputReferences() {
    // Store all input and textarea elements
    inputElements = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], input:not([type])'));
    textareaElements = Array.from(document.querySelectorAll('textarea'));
  }

  function restoreInputFunctionality() {
    // Re-focus and re-initialize input fields after print
    setTimeout(() => {
      // Restore focus capability and event listeners for input fields
      inputElements.forEach(input => {
        if (input && input.parentNode) {
          // Force re-focus capability
          input.blur();
          input.focus();
          input.blur();
          
          // Re-trigger any stored event listeners
          const storedListeners = originalEventListeners.get(input);
          if (storedListeners) {
            storedListeners.forEach(listenerInfo => {
              input.addEventListener(listenerInfo.type, listenerInfo.listener, listenerInfo.options);
            });
          }
        }
      });

      // Same for textarea elements
      textareaElements.forEach(textarea => {
        if (textarea && textarea.parentNode) {
          textarea.blur();
          textarea.focus();
          textarea.blur();
          
          const storedListeners = originalEventListeners.get(textarea);
          if (storedListeners) {
            storedListeners.forEach(listenerInfo => {
              textarea.addEventListener(listenerInfo.type, listenerInfo.listener, listenerInfo.options);
            });
          }
        }
      });
    }, 100);
  }

  function enhancePrintFunction(originalPrintFn) {
    return function(...args) {
      // Store input references before print
      storeInputReferences();
      
      // Call original print function
      const result = originalPrintFn.apply(this, args);
      
      // Restore input functionality after print
      restoreInputFunctionality();
      
      return result;
    };
  }

  // Override window.print to handle the restoration
  const originalWindowPrint = window.print;
  window.print = enhancePrintFunction(originalWindowPrint);

  // Listen for afterprint event (when user cancels or completes print)
  window.addEventListener('afterprint', restoreInputFunctionality);
  
  // Listen for beforeprint event to prepare
  window.addEventListener('beforeprint', storeInputReferences);

  // For cases where print is called programmatically (like in QR code forms)
  const originalOpenWindow = window.open;
  window.open = function(url, target, features) {
    const newWindow = originalOpenWindow.call(this, url, target, features);
    
    if (newWindow && target === '_blank') {
      // If this is a print window (detected by common print patterns)
      const originalWrite = newWindow.document.write;
      newWindow.document.write = function(content) {
        const result = originalWrite.apply(this, arguments);
        
        // If content includes print() call, prepare for restoration
        if (content.includes('window.print()') || content.includes('window.onload')) {
          // Schedule restoration for after the print window closes
          setTimeout(restoreInputFunctionality, 500);
        }
        
        return result;
      };
    }
    
    return newWindow;
  };

  // Initialize on page load
  document.addEventListener('DOMContentLoaded', storeInputReferences);
  
  // Re-initialize when DOM changes (for dynamic content)
  if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
      let shouldUpdate = false;
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1) { // Element node
              if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA' || 
                  node.querySelector && (node.querySelector('input') || node.querySelector('textarea'))) {
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

})();