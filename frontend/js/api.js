class APIClient {
    constructor() {
        this.baseURL = '/api';
        
        // 从URL参数中获取访问token
        const urlParams = new URLSearchParams(window.location.search);
        this.token = urlParams.get('token');
        
        console.log('[API] baseURL:', this.baseURL);
        console.log('[API] Token:', this.token ? '已配置' : '未配置');
    }

    async query(data) {
        let url = `${this.baseURL}/query`;
        
        // 如果有token，添加到URL参数中
        if (this.token) {
            url += `?token=${this.token}`;
        }
        
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

            const text = await response.text();
            console.log('[API] 响应原始数据:', text);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = JSON.parse(text);
            return result;
        } catch (error) {
            console.error('[API] 请求错误:', error);
            throw error;
        }
    }
}

// 创建API客户端实例
const apiClient = new APIClient();
