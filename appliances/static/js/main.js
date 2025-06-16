import { initializeModal } from './deviceForm.js';
import { initializeViewToggle } from './viewToggle.js';
import { initializeStatusToggles } from './statusToggle.js';
import { initializeSearch } from './searchDevices.js';
import { initializeAnimations } from './animations.js';
import { initializeFormElements } from './form.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form elements first
    initializeFormElements();
    
    initializeModal();
    initializeViewToggle();
    initializeStatusToggles();
    initializeSearch();
    initializeAnimations();
});