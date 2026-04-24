class AdminAPI {
    constructor() {
        this.baseURL = '/api/admin';
    }

    async request(method, path, data) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (data) options.body = JSON.stringify(data);
        const response = await fetch(`${this.baseURL}${path}`, options);
        const result = await response.json();
        if (!result.success && response.status === 401) {
            window.location.href = '/admin/login.html';
            return;
        }
        return result;
    }

    async login(username, password) {
        return this.request('POST', '/auth/login', { username, password });
    }

    async logout() {
        return this.request('POST', '/auth/logout');
    }

    async checkAuth() {
        return this.request('GET', '/auth/check');
    }

    async setup(username, password) {
        return this.request('POST', '/init/setup', { username, password });
    }

    async getDatasources() {
        return this.request('GET', '/datasources');
    }

    async addDatasource(data) {
        return this.request('POST', '/datasources', data);
    }

    async updateDatasource(id, data) {
        return this.request('PUT', `/datasources/${id}`, data);
    }

    async deleteDatasource(id) {
        return this.request('DELETE', `/datasources/${id}`);
    }

    async testConnection(data) {
        return this.request('POST', '/datasources/test', data);
    }

    async getSettings() {
        return this.request('GET', '/settings');
    }

    async changePassword(oldPassword, newPassword) {
        return this.request('PUT', '/settings/password', { old_password: oldPassword, new_password: newPassword });
    }

    async updateToken(token) {
        return this.request('PUT', '/settings/token', { token });
    }

    async getDashboardStats() {
        return this.request('GET', '/dashboard/stats');
    }
}

const adminAPI = new AdminAPI();
