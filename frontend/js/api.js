class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
    }

    async query(data) {
        try {
            const response = await fetch(`${this.baseURL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('网络请求失败');
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }
}

// 创建API客户端实例
const apiClient = new APIClient();