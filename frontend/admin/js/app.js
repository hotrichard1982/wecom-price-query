async function checkLogin() {
    const result = await adminAPI.checkAuth();
    if (!result || !result.success) {
        window.location.href = '/admin/login.html';
        return null;
    }
    return result;
}

async function logout() {
    await adminAPI.logout();
    window.location.href = '/admin/login.html';
}

function showToast(message, type) {
    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-emerald-500'
        : type === 'error' ? 'bg-red-500'
        : type === 'warning' ? 'bg-amber-500'
        : 'bg-blue-500';
    toast.className = `fixed top-4 right-4 px-5 py-3 rounded-lg shadow-lg text-white z-50 animate-slide-in ${bgColor}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function formatDate(isoString) {
    if (!isoString) return '-';
    const d = new Date(isoString);
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}
