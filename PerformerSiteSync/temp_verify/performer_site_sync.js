/**
 * Performer/Site Sync Plugin UI Enhancement
 * Provides better user experience for plugin task buttons
 */

(function() {
    'use strict';

    // Plugin configuration
    const PLUGIN_ID = 'PerformerSiteSync';
    const PLUGIN_NAME = 'Performer/Site Sync';

    // Task button configurations with enhanced UI
    const TASK_CONFIGS = {
        'Update All Performers': {
            icon: '🔄',
            confirmMessage: 'This will update ALL performers in your library. This may take a long time. Continue?',
            progressMessage: 'Updating all performers...',
            className: 'btn-primary'
        },
        'Update Single Performer': {
            icon: '👤',
            confirmMessage: 'Update this performer with data from external sources?',
            progressMessage: 'Updating performer...',
            className: 'btn-info'
        },
        'Sync Favorites from All Sources': {
            icon: '⭐',
            confirmMessage: 'Sync favorite performers from all configured sources?',
            progressMessage: 'Syncing favorites...',
            className: 'btn-warning'
        },
        'Sync StashDB Favorites': {
            icon: '🗃️',
            confirmMessage: 'Sync favorite performers from StashDB?',
            progressMessage: 'Syncing StashDB favorites...',
            className: 'btn-secondary'
        },
        'Sync TPDB Favorites': {
            icon: '🎬',
            confirmMessage: 'Sync favorite performers from ThePornDB?',
            progressMessage: 'Syncing TPDB favorites...',
            className: 'btn-secondary'
        },
        'Sync FansDB Favorites': {
            icon: '💫',
            confirmMessage: 'Sync favorite performers from FansDB?',
            progressMessage: 'Syncing FansDB favorites...',
            className: 'btn-secondary'
        },
        'Test Connections': {
            icon: '🔧',
            confirmMessage: 'Test connections to all configured external sources?',
            progressMessage: 'Testing connections...',
            className: 'btn-success'
        },
        'Clear Cache': {
            icon: '🗑️',
            confirmMessage: 'Clear all cached data? This will force fresh data retrieval on next sync.',
            progressMessage: 'Clearing cache...',
            className: 'btn-danger'
        },
        'Generate Sync Report': {
            icon: '📊',
            confirmMessage: 'Generate a detailed sync status report?',
            progressMessage: 'Generating report...',
            className: 'btn-info'
        },
        'Validate Configuration': {
            icon: '✅',
            confirmMessage: 'Validate plugin configuration and connections?',
            progressMessage: 'Validating configuration...',
            className: 'btn-light'
        }
    };

    // Enhanced task button creation
    function enhanceTaskButtons() {
        const taskButtons = document.querySelectorAll('button[data-task]');
        
        taskButtons.forEach(button => {
            const taskName = button.getAttribute('data-task');
            const config = TASK_CONFIGS[taskName];
            
            if (config) {
                // Add icon and styling
                if (!button.querySelector('.task-icon')) {
                    const icon = document.createElement('span');
                    icon.className = 'task-icon';
                    icon.textContent = config.icon + ' ';
                    button.insertBefore(icon, button.firstChild);
                }
                
                // Add CSS class
                button.className = `btn ${config.className} task-button`;
                
                // Add confirmation dialog
                button.addEventListener('click', function(e) {
                    if (config.confirmMessage) {
                        if (!confirm(config.confirmMessage)) {
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }
                    }
                    
                    // Show progress message
                    if (config.progressMessage) {
                        showProgressMessage(config.progressMessage);
                    }
                });
            }
        });
    }

    // Progress message display
    function showProgressMessage(message) {
        // Remove existing progress messages
        const existingProgress = document.querySelector('.sync-progress-message');
        if (existingProgress) {
            existingProgress.remove();
        }
        
        // Create new progress message
        const progressDiv = document.createElement('div');
        progressDiv.className = 'sync-progress-message alert alert-info';
        progressDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>${message}</span>
            </div>
        `;
        
        // Insert after plugin title
        const pluginSection = document.querySelector(`h2:contains("${PLUGIN_NAME}")`);
        if (pluginSection && pluginSection.parentNode) {
            pluginSection.parentNode.insertBefore(progressDiv, pluginSection.nextSibling);
        }
    }

    // Add custom CSS styles
    function addCustomStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .task-button {
                margin: 2px;
                min-width: 140px;
                display: inline-flex;
                align-items: center;
                justify-content: flex-start;
            }
            
            .task-icon {
                font-size: 1.1em;
                margin-right: 5px;
            }
            
            .sync-progress-message {
                margin: 10px 0;
                border-radius: 5px;
            }
            
            .sync-progress-message .spinner-border-sm {
                width: 1rem;
                height: 1rem;
            }
            
            /* Task button grid layout */
            .plugin-tasks {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 8px;
                margin: 15px 0;
            }
            
            .plugin-tasks .task-button {
                width: 100%;
                justify-content: center;
            }
            
            /* Plugin section styling */
            .plugin-section h4 {
                color: #007bff;
                border-bottom: 2px solid #007bff;
                padding-bottom: 5px;
                margin-bottom: 15px;
            }
        `;
        document.head.appendChild(style);
    }

    // Status indicator for connection test results
    function createStatusIndicator(status, responseTime = null) {
        const indicator = document.createElement('span');
        indicator.className = `status-indicator status-${status}`;
        
        let icon, text, className;
        switch(status) {
            case 'connected':
                icon = '✅';
                text = `Connected${responseTime ? ` (${responseTime}ms)` : ''}`;
                className = 'text-success';
                break;
            case 'failed':
            case 'error':
                icon = '❌';
                text = 'Failed';
                className = 'text-danger';
                break;
            default:
                icon = '⏳';
                text = 'Testing...';
                className = 'text-warning';
        }
        
        indicator.innerHTML = `<span class="${className}">${icon} ${text}</span>`;
        return indicator;
    }

    // Enhanced logging display
    function enhanceLogDisplay() {
        const logContainer = document.querySelector('.log-container, .plugin-log');
        if (logContainer) {
            logContainer.style.maxHeight = '400px';
            logContainer.style.overflowY = 'auto';
            logContainer.style.border = '1px solid #dee2e6';
            logContainer.style.borderRadius = '5px';
            logContainer.style.padding = '10px';
            logContainer.style.backgroundColor = '#f8f9fa';
        }
    }

    // Initialize UI enhancements
    function init() {
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        addCustomStyles();
        enhanceTaskButtons();
        enhanceLogDisplay();
        
        // Re-enhance buttons when new content is loaded
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    setTimeout(enhanceTaskButtons, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Start initialization
    init();

    // Expose functions for potential use by other scripts
    window.PerformerSiteSyncUI = {
        enhanceTaskButtons,
        showProgressMessage,
        createStatusIndicator
    };

})();
