/**
 * Smart File Organizer Pro - Main UI Logic
 */

// Shared UI Helper
const ui = {
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        
        let bgColor = 'bg-blue-500';
        let icon = 'fa-info-circle';
        
        if (type === 'success') { bgColor = 'bg-green-500'; icon = 'fa-check-circle'; }
        if (type === 'error') { bgColor = 'bg-red-500'; icon = 'fa-exclamation-circle'; }
        if (type === 'warning') { bgColor = 'bg-yellow-500'; icon = 'fa-exclamation-triangle'; }

        toast.className = `flex items-center w-full max-w-xs p-4 mb-4 text-white ${bgColor} rounded-lg shadow-lg transform transition-all duration-300 translate-x-full opacity-0`;
        toast.innerHTML = `
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg bg-white/20">
                <i class="fas ${icon}"></i>
            </div>
            <div class="ml-3 text-sm font-medium z-50 text-white">${message}</div>
        `;

        container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        });

        // Remove after 3s
        setTimeout(() => {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    },

    formatDate(isoString) {
        if(!isoString) return '-';
        const d = new Date(isoString);
        return d.toLocaleString();
    }
};

// Initialize Theme
function initTheme() {
    if (appState.theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();

    // Check auth on protected pages
    const protectedPaths = ['/dashboard', '/scanner', '/organizer', '/duplicates', '/large-files', '/rules', '/logs', '/settings', '/'];
    const currentPath = window.location.pathname;
    
    if (!appState.token && protectedPaths.some(p => p === currentPath)) {
        window.location.href = '/login';
        return;
    }

    // Set greeting
    const greetingEl = document.getElementById('userGreeting');
    if (greetingEl && appState.user) {
        greetingEl.textContent = `Hello, ${appState.user.username}`;
    }

    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            if(window.Chart) { location.reload(); }
        });
    }

    // Sidebar Toggle (Mobile)
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('openSidebar');
    const closeSidebarBtn = document.getElementById('closeSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function toggleSidebar() {
        if (!sidebar) return;
        sidebar.classList.toggle('-translate-x-full');
        if (sidebarOverlay) sidebarOverlay.classList.toggle('hidden');
    }

    if (openSidebarBtn) openSidebarBtn.addEventListener('click', toggleSidebar);
    if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);

    // Active link highlighting
    document.querySelectorAll('.nav-item').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/dashboard')) {
            link.classList.add('bg-indigo-50', 'text-indigo-600', 'dark:bg-indigo-900/30', 'dark:text-indigo-400', 'font-semibold');
            link.classList.remove('text-gray-700', 'dark:text-gray-300');
        }
    });

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        });
    }
});
