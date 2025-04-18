// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Add any initialization logic here
    console.log('ELI-Online application initialized');
    
    // Example: Load services dynamically
    loadServices();
}

async function loadServices() {
    try {
        const servicesContainer = document.querySelector('.services-grid');
        if (!servicesContainer) return;

        // In the future, this could fetch from an API endpoint
        const services = [
            { title: 'Service 1', description: 'Description of service 1' },
            { title: 'Service 2', description: 'Description of service 2' },
            { title: 'Service 3', description: 'Description of service 3' }
        ];

        services.forEach(service => {
            const serviceElement = createServiceElement(service);
            servicesContainer.appendChild(serviceElement);
        });
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function createServiceElement(service) {
    const div = document.createElement('div');
    div.className = 'service-item';
    div.innerHTML = `
        <h4>${service.title}</h4>
        <p>${service.description}</p>
    `;
    return div;
} 