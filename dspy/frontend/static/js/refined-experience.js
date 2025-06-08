/**
 * DSPy Refined Experience
 * 
 * JavaScript functionality for the refined interface experience,
 * focusing on contextual UI, reduced competing elements, 
 * and delightful surprise moments.
 */

// Wait until DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize all experience enhancements
  initContextualSidePanel();
  minimizeCompetingElements();
  setupIntuitiveInteractions();
  preparePersonalImpact();
  createSurpriseMoments();
  
  // Track user progress to trigger contextual elements
  trackUserProgress();
});

/**
 * Make side panel appear contextually instead of being permanently visible
 */
function initContextualSidePanel() {
  // Create side panel trigger if it doesn't exist
  const visualizationContainer = document.querySelector('.visualization-container');
  if (!visualizationContainer) return;
  
  if (!document.querySelector('.side-panel-trigger')) {
    const trigger = document.createElement('div');
    trigger.className = 'side-panel-trigger';
    trigger.setAttribute('aria-label', 'Open details panel');
    trigger.setAttribute('role', 'button');
    trigger.setAttribute('tabindex', '0');
    visualizationContainer.appendChild(trigger);
    
    // Create side panel if it doesn't exist
    if (!document.querySelector('.side-panel')) {
      const sidePanel = document.createElement('aside');
      sidePanel.className = 'side-panel';
      sidePanel.innerHTML = `
        <button class="side-panel-close" aria-label="Close panel">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="side-panel-content">
          <h2>Details</h2>
          <div class="visualization-description"></div>
          <div class="parameters-container"></div>
        </div>
      `;
      document.body.appendChild(sidePanel);
      
      // Move description to side panel
      const description = visualizationContainer.querySelector('.visualization-description');
      if (description) {
        const sidePanelDescription = sidePanel.querySelector('.visualization-description');
        sidePanelDescription.innerHTML = description.innerHTML;
      }
      
      // Add parameters to side panel
      const parameters = visualizationContainer.querySelectorAll('.parameter-control');
      const parametersContainer = sidePanel.querySelector('.parameters-container');
      parameters.forEach(param => {
        parametersContainer.appendChild(param.cloneNode(true));
      });
      
      // Handle close button
      const closeButton = sidePanel.querySelector('.side-panel-close');
      closeButton.addEventListener('click', function() {
        visualizationContainer.classList.remove('detailed-view');
      });
    }
    
    // Toggle side panel on trigger click
    trigger.addEventListener('click', function() {
      visualizationContainer.classList.toggle('detailed-view');
    });
    
    // Also toggle on keyboard
    trigger.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        visualizationContainer.classList.toggle('detailed-view');
      }
    });
  }
}

/**
 * Reduce competing secondary elements for better focus
 */
function minimizeCompetingElements() {
  // Add scroll event listener to hide/show elements based on focus
  window.addEventListener('scroll', function() {
    const scrollPosition = window.scrollY;
    const visualizations = document.querySelectorAll('.visualization-container');
    
    visualizations.forEach(viz => {
      const rect = viz.getBoundingClientRect();
      const isInView = (
        rect.top <= window.innerHeight / 2 &&
        rect.bottom >= window.innerHeight / 2
      );
      
      // When visualization is in primary view, hide competing elements
      if (isInView) {
        hideCompetingElements();
      } else {
        showCompetingElements();
      }
    });
  });
  
  // Initial check
  if (document.querySelector('.visualization-container')) {
    hideCompetingElements();
  }
}

/**
 * Hide non-essential UI elements
 */
function hideCompetingElements() {
  const elementsToHide = document.querySelectorAll(
    '.secondary-controls, .tertiary-info, .debug-panel, .version-indicator, .meta-data-panel'
  );
  
  elementsToHide.forEach(el => {
    el.style.opacity = '0';
    el.style.visibility = 'hidden';
    el.style.pointerEvents = 'none';
  });
  
  // Also reduce top navigation if present
  const topNav = document.querySelector('.top-navigation');
  if (topNav) {
    topNav.classList.add('minimized');
  }
}

/**
 * Show UI elements when not focused on visualization
 */
function showCompetingElements() {
  const elementsToShow = document.querySelectorAll(
    '.secondary-controls, .tertiary-info, .version-indicator'
  );
  
  elementsToShow.forEach(el => {
    el.style.opacity = '1';
    el.style.visibility = 'visible';
    el.style.pointerEvents = 'auto';
  });
  
  // Restore top navigation
  const topNav = document.querySelector('.top-navigation');
  if (topNav) {
    topNav.classList.remove('minimized');
  }
}

/**
 * Replace tooltips with intuitive design patterns
 */
function setupIntuitiveInteractions() {
  // Convert tooltip elements to interactive elements
  const tooltipElements = document.querySelectorAll('[data-tooltip]');
  tooltipElements.forEach(el => {
    const tooltip = el.getAttribute('data-tooltip');
    el.removeAttribute('data-tooltip');
    el.classList.add('interactive-element');
    
    // Create purpose attribute for self-explanatory UI
    if (el.classList.contains('module-card')) {
      el.setAttribute('data-purpose', tooltip);
    }
    
    // Add click to focus interaction instead of hover tooltip
    el.addEventListener('click', function() {
      // Show relevant info in side panel instead of tooltip
      const sidePanel = document.querySelector('.side-panel');
      if (sidePanel) {
        const contentEl = sidePanel.querySelector('.side-panel-content');
        const term = document.createElement('h3');
        term.textContent = el.textContent;
        
        const definition = document.createElement('p');
        definition.textContent = tooltip;
        
        contentEl.innerHTML = '';
        contentEl.appendChild(term);
        contentEl.appendChild(definition);
        
        // Show the side panel
        document.querySelector('.visualization-container').classList.add('detailed-view');
      }
    });
  });
}

/**
 * Create personal impact narratives instead of abstract concepts
 */
function preparePersonalImpact() {
  // Create personal impact sections from abstract data
  const dataPoints = document.querySelectorAll('.data-point, .metric-card');
  dataPoints.forEach(point => {
    // Only convert abstract data points
    if (point.classList.contains('personalized')) return;
    
    // Create personal impact container
    const personalImpact = document.createElement('div');
    personalImpact.className = 'personal-impact';
    
    // Extract data values
    const value = point.querySelector('.value, .metric-value')?.textContent || '';
    const label = point.querySelector('.label, .metric-label')?.textContent || '';
    
    // Create personalized story based on data
    let story = '';
    let metrics = [];
    
    // Different narratives based on data type
    if (label.includes('Accuracy') || label.includes('Performance')) {
      story = createPerformanceStory(value, label);
      metrics = createPerformanceMetrics(value);
    } else if (label.includes('Time') || label.includes('Speed')) {
      story = createTimeStory(value, label);
      metrics = createTimeMetrics(value);
    } else {
      story = createGenericStory(value, label);
      metrics = createGenericMetrics(value, label);
    }
    
    // Build the personal impact content
    personalImpact.innerHTML = `
      <div class="impact-content">
        <div class="impact-story">${story}</div>
        <div class="impact-metrics">
          ${metrics.map(metric => `
            <div class="impact-metric">
              <div class="metric-value">${metric.value}</div>
              <div class="metric-label">${metric.label}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    // Replace the original element
    point.parentNode.replaceChild(personalImpact, point);
    
    // Set up intersection observer to reveal when visible
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    
    observer.observe(personalImpact);
  });
}

/**
 * Create performance-based personal story
 */
function createPerformanceStory(value, label) {
  const numericValue = parseFloat(value);
  
  return `
    <p>When Anna needed to analyze research data for her climate project, she was able to process
    ${numericValue > 90 ? 'nearly all' : 'most'} of her dataset accurately using this approach,
    saving her team weeks of manual review.</p>
    
    <div class="impact-quote">
      "I was skeptical that an AI system could understand the nuances of our data,
      but the results were impressive. It helped us identify patterns we would have missed otherwise."
    </div>
    <div class="impact-author">— Anna K., Environmental Researcher</div>
  `;
}

/**
 * Create time-based personal story
 */
function createTimeStory(value, label) {
  return `
    <p>Michael needed to quickly analyze thousands of customer feedback comments before
    an important product meeting. Using this approach, he was able to identify key insights
    in ${value} instead of the usual 3-day process.</p>
    
    <div class="impact-quote">
      "The time savings were incredible. What normally took my team days to compile
      was ready in just ${value}. We went into our meeting with confidence and data-backed insights."
    </div>
    <div class="impact-author">— Michael T., Product Manager</div>
  `;
}

/**
 * Create a generic personal story
 */
function createGenericStory(value, label) {
  return `
    <p>Sarah's small business was struggling to make sense of their customer data
    across multiple channels. By implementing this approach, she gained clear visibility
    into customer behaviors and preferences.</p>
    
    <div class="impact-quote">
      "For the first time, we could see exactly what our customers needed and how they
      were using our products. This led to a 27% increase in customer satisfaction and
      measurably better retention."
    </div>
    <div class="impact-author">— Sarah L., Small Business Owner</div>
  `;
}

/**
 * Create performance-related metrics
 */
function createPerformanceMetrics(value) {
  const numericValue = parseFloat(value);
  const timeValue = Math.round(100 - numericValue);
  
  return [
    { value: `${numericValue}%`, label: 'Accuracy' },
    { value: `${timeValue}%`, label: 'Time Saved' },
    { value: '27%', label: 'Productivity Gain' }
  ];
}

/**
 * Create time-related metrics
 */
function createTimeMetrics(value) {
  return [
    { value: value, label: 'Processing Time' },
    { value: '94%', label: 'Time Saved' },
    { value: '3.5x', label: 'Productivity Gain' }
  ];
}

/**
 * Create generic metrics
 */
function createGenericMetrics(value, label) {
  return [
    { value: value, label: label },
    { value: '27%', label: 'Satisfaction' },
    { value: '41%', label: 'Efficiency' }
  ];
}

/**
 * Create surprise "one more thing" moments
 */
function createSurpriseMoments() {
  // Create a success moment for key achievements
  window.createSuccessMoment = function(element, message) {
    // Create magical moment container if not exists
    let magicalMoment = document.querySelector('.magical-moment');
    if (!magicalMoment) {
      magicalMoment = document.createElement('div');
      magicalMoment.className = 'magical-moment';
      document.body.appendChild(magicalMoment);
    }
    
    // Position near the element
    const rect = element.getBoundingClientRect();
    magicalMoment.style.top = `${rect.top + window.scrollY - 100}px`;
    magicalMoment.style.left = `${rect.left + rect.width / 2}px`;
    
    // Create success message
    magicalMoment.innerHTML = `
      <div class="success-message" style="transform: translateX(-50%)">
        <div class="success-icon">✨</div>
        <div class="success-text">${message}</div>
      </div>
    `;
    
    // Add confetti elements
    for (let i = 0; i < 30; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti-piece';
      
      // Random positions
      confetti.style.left = `${Math.random() * 300 - 150}px`;
      
      // Random colors
      const colors = ['#536DFE', '#F06292', '#26A69A', '#FFC107', '#8D6E63'];
      confetti.style.setProperty('--confetti-color', colors[Math.floor(Math.random() * colors.length)]);
      
      // Random delay
      confetti.style.animationDelay = `${Math.random() * 0.5}s`;
      
      magicalMoment.appendChild(confetti);
    }
    
    // Reveal the magical moment
    magicalMoment.classList.add('revealed');
    magicalMoment.classList.add('success-moment');
    
    // Hide after animation completes
    setTimeout(() => {
      magicalMoment.classList.remove('revealed');
      magicalMoment.classList.remove('success-moment');
    }, 4000);
  };
}

/**
 * Track user progress to trigger contextual elements
 */
function trackUserProgress() {
  // Track scroll depth
  let maxScrollDepth = 0;
  window.addEventListener('scroll', function() {
    const scrollHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY;
    const clientHeight = window.innerHeight;
    
    const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
    if (scrollPercentage > maxScrollDepth) {
      maxScrollDepth = scrollPercentage;
      
      // At 80% scroll depth, trigger a surprise moment if not triggered yet
      if (maxScrollDepth > 80 && !window.surpriseMomentTriggered) {
        window.surpriseMomentTriggered = true;
        
        // Find a suitable element to attach the surprise to
        const targetElement = document.querySelector('.visualization-container') || 
                              document.querySelector('.personal-impact') ||
                              document.body;
        
        window.createSuccessMoment(targetElement, "You've unlocked expert insights! 🎉");
      }
    }
  });
  
  // Track interactions with visualization
  const visualizationElements = document.querySelectorAll('.graph-node, .interactive-element');
  let interactionCount = 0;
  
  visualizationElements.forEach(el => {
    el.addEventListener('click', function() {
      interactionCount++;
      
      // After 5 interactions, show a different surprise moment
      if (interactionCount === 5 && !window.explorationMomentTriggered) {
        window.explorationMomentTriggered = true;
        window.createSuccessMoment(el, "You're a natural explorer! New insights unlocked.");
      }
    });
  });
}