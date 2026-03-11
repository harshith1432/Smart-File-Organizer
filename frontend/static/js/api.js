/**
 * Smart File Organizer Pro - Core API and State
 */

// Global Application State
const appState = {
    theme: localStorage.getItem('theme') || 'dark',
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null
};

// API Wrapper
const api = {
    async request(endpoint, options = {}) {
        const url = `/api${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (appState.token) {
            headers['Authorization'] = `Bearer ${appState.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized
            if (response.status === 401 && !endpoint.includes('/auth/login')) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Server Error');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) { return this.request(endpoint); },
    post(endpoint, body) { return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) }); },
    delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }); }
};
