class APIClient {
    constructor() {
        this.baseURL = '/api';
        console.log('[API] baseURL:', this.baseURL);
        console.log('[API] window.location:', window.location.href);
    }

    async query(data) {
        const url = `${this.baseURL}/query`;
        console.log('[API] 请求URL:', url);
        console.log('[API] 请求数据:', JSON.stringify(data, null, 2));

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            console.log('[API] 响应状态:', response.status, response.statusText);
            console.log('[API] 响应头:', Object.fromEntries(response.headers.entries()));

            const text = await response.text();
            console.log('[API] 响应原始数据:', text);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = JSON.parse(text);
            console.log('[API] 解析后的JSON:', JSON.stringify(result, null, 2));
            return result;
        } catch (error) {
            console.error('[API] 请求错误:', error);
            throw error;
        }
    }
}

// 创建API客户端实例
const apiClient = new APIClient();
