import { initializeModal } from './deviceForm.js';
import { initializeViewToggle } from './viewToggle.js';
import { initializeStatusToggles } from './statusToggle.js';
import { initializeSearch } from './searchDevices.js';
import { initializeAnimations } from './animations.js';

document.addEventListener('DOMContentLoaded', function() {
    initializeModal();
    initializeViewToggle();
    initializeStatusToggles();
    initializeSearch();
    initializeAnimations();
});