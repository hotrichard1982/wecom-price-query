document.addEventListener('DOMContentLoaded', function() {
    // 元素获取
    const loading = document.getElementById('loading');
    const app = document.getElementById('app');
    const queryForm = document.getElementById('query-form');
    const result = document.getElementById('result');
    const resultCount = document.getElementById('result-count');
    const resultList = document.getElementById('result-list');
    const powerSelect = document.getElementById('power');
    const engineModelSelect = document.getElementById('engine-model');
    const generatorModelSelect = document.getElementById('generator-model');
    const clearBtn = document.getElementById('clear-btn');
    const productNameInput = document.getElementById('product-name');

    // 存储所有产品数据
    let allProducts = [];

    // HTML转义函数，防止XSS攻击
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const str = String(text);
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // 显示应用，隐藏加载动画
    setTimeout(() => {
        loading.classList.add('hidden');
        app.classList.remove('hidden');
        // 加载下拉菜单数据
        loadAllProducts();
    }, 1000);

    // 加载所有产品数据
    async function loadAllProducts() {
        try {
            // 调用API获取所有产品数据
            const response = await apiClient.query({});
            
            if (response.success) {
                allProducts = response.data;
                // 填充下拉菜单
                populateDropdowns();
            }
        } catch (error) {
            console.error('加载产品数据失败:', error);
        }
    }

    // 填充下拉菜单
    function populateDropdowns() {
        // 提取唯一值
        const powers = [...new Set(allProducts.map(item => item['功率(KVA/KW)']).filter(Boolean))];
        const engineModels = [...new Set(allProducts.map(item => item['柴油发动机型号']).filter(Boolean))];
        const generatorModels = [...new Set(allProducts.map(item => item['发电机型号']).filter(Boolean))];

        // 填充功率下拉菜单
        powers.forEach(power => {
            const option = document.createElement('option');
            option.value = power;
            option.textContent = power;
            powerSelect.appendChild(option);
        });

        // 填充柴油发动机型号下拉菜单
        engineModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            engineModelSelect.appendChild(option);
        });

        // 填充发电机型号下拉菜单
        generatorModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            generatorModelSelect.appendChild(option);
        });
    }

    // 表单提交处理
    queryForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // 获取表单数据
        const productName = document.getElementById('product-name').value;
        const power = document.getElementById('power').value;
        const engineModel = document.getElementById('engine-model').value;
        const generatorModel = document.getElementById('generator-model').value;

        // 前端筛选数据
        const filteredProducts = filterProducts(allProducts, {
            productName,
            power,
            engineModel,
            generatorModel
        });

        // 渲染查询结果
        renderResult(filteredProducts);
    });

    // 清空按钮点击处理
    clearBtn.addEventListener('click', function() {
        // 清空所有输入项
        productNameInput.value = '';
        powerSelect.value = '';
        engineModelSelect.value = '';
        generatorModelSelect.value = '';
        
        // 隐藏查询结果
        result.classList.add('hidden');
        resultList.innerHTML = '';
    });

    // 前端筛选产品
    function filterProducts(products, filters) {
        return products.filter(product => {
            // 产品名筛选
            if (filters.productName && !product['产品名']?.includes(filters.productName)) {
                return false;
            }
            // 功率筛选
            if (filters.power && product['功率(KVA/KW)'] !== filters.power) {
                return false;
            }
            // 柴油发动机型号筛选
            if (filters.engineModel && product['柴油发动机型号'] !== filters.engineModel) {
                return false;
            }
            // 发电机型号筛选
            if (filters.generatorModel && product['发电机型号'] !== filters.generatorModel) {
                return false;
            }
            return true;
        });
    }

    // 渲染查询结果
    function renderResult(data) {
        // 显示结果区域
        result.classList.remove('hidden');

        // 清空结果列表
        resultList.innerHTML = '';

        // 渲染每条记录
        data.forEach(item => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            // 构建结果内容
            let infoHTML = '<table class="product-table">';
            
            // 遍历所有字段，排除隐藏字段
            for (const [key, value] of Object.entries(item)) {
                if (key !== '产品ID' && key !== '上浮指数' && key !== '成本' && key !== '产品图片' && key !== '报价') {
                    let displayValue = value || 'N/A';
                    // 处理数组类型的值
                    if (Array.isArray(displayValue)) {
                        displayValue = displayValue.map(v => v.text || v).join(', ');
                    }
                    infoHTML += `<tr><td class="param-name">${escapeHtml(key)}</td><td class="param-value">${escapeHtml(displayValue)}</td></tr>`;
                }
            }
            
            infoHTML += '</table>';

            // 构建卡片内容
            let cardHTML = '';
            
            // 添加产品图片
            if (item['产品图片']) {
                cardHTML += `<div class="product-image">
                    <img src="${escapeHtml(item['产品图片'])}" alt="${escapeHtml(item['产品名'] || '产品图片')}">
                </div>`;
            }
            
            // 添加产品信息
            cardHTML += `
                <h3>${escapeHtml(item['产品名'] || 'N/A')}</h3>
                <div class="price">
                    报价: ¥${escapeHtml(item['报价'] || 0)}
                </div>
                <div class="info">
                    ${infoHTML}
                </div>
            `;
            
            resultItem.innerHTML = cardHTML;

            // 添加到结果列表
            resultList.appendChild(resultItem);
        });
    }
});