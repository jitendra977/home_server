import initializeViewToggle from './viewToggle.js';
import initializeStatusToggles from './statusToggle.js';
import initializeSearch from './searchDevices.js';
import initializeDeviceForm from './deviceForm.js';
import initializeAnimations from './animations.js';

document.addEventListener('DOMContentLoaded', function () {
    initializeViewToggle();
    initializeStatusToggles();
    initializeSearch();
    initializeDeviceForm();
    initializeAnimations();
});