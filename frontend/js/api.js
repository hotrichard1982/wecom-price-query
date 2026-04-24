class APIClient {
    constructor() {
        this.baseURL = '/api/query';
        this.datasourceId = null;
        this.token = '';
        
        const urlParams = new URLSearchParams(window.location.search);
        this.token = urlParams.get('token') || '';
    }

    async init() {
        try {
            const resp = await fetch(`${this.baseURL}/datasources`);
            const result = await resp.json();
            if (result.success && result.data && result.data.length > 0) {
                this.datasourceId = result.data[0].id;
                if (result.token && !this.token) {
                    this.token = result.token;
                }
            }
            console.log('[API] 初始化完成, 数据源:', this.datasourceId, 'Token:', this.token ? '已配置' : '未配置');
        } catch (e) {
            console.error('[API] 初始化失败:', e);
        }
    }

    async query(data) {
        let url = `${this.baseURL}/query`;
        const params = [];
        if (this.datasourceId) {
            params.push(`datasource_id=${this.datasourceId}`);
        }
        if (this.token) {
            params.push(`token=${this.token}`);
        }
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        console.log('[API] 请求URL:', url);
        console.log('[API] 请求数据:', JSON.stringify(data, null, 2));

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            console.log('[API] 响应状态:', response.status);
            const text = await response.text();
            console.log('[API] 响应原始数据:', text);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return JSON.parse(text);
        } catch (error) {
            console.error('[API] 请求错误:', error);
            throw error;
        }
    }
}

const apiClient = new APIClient();
