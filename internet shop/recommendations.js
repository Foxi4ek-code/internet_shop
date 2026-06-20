const API_URL = 'http://localhost:8000';

class PersonalizedRecommendations {
    constructor(containerId, userId) {
        this.container = document.getElementById(containerId);
        this.userId = userId;
    }
    async fetch() {
        try {
            const response = await fetch(`${API_URL}/recommendations/personalized`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    n: 10
                })
            });
            if (!response.ok) {
                throw new Error('Ошибка загрузки рекомендаций');
            }
            const recommendations = await response.json();
            this.render(recommendations);
        } catch (error) {
            console.error('Ошибка:', error);
            this.renderError();
        }
    }
    render(recommendations) {
        if (!this.container) return;
        const html = `
            <div class="rec-scroll-wrapper">
                <div class="rec-scroll-header">
                    <h3>Рекомендовано для вас</h3>
                    <div class="rec-scroll-arrows">
                        <button class="rec-scroll-btn rec-scroll-prev" data-track="rec-track-personalized">❮</button>
                        <button class="rec-scroll-btn rec-scroll-next" data-track="rec-track-personalized">❯</button>
                    </div>
                </div>
                <div class="rec-scroll-track" id="rec-track-personalized">
                    ${recommendations.map(product => this.createProductCard(product)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
        this.initScrollArrows();
    }
    createProductCard(product) {
        return `
            <div class="rec-scroll-card" data-product-name="${product.name}" data-product-price="${product.price}" data-product-image="${product.image}" data-product-description="${product.description}">
                <img src="${product.image}" alt="${product.name}">
                <div class="rec-scroll-card-info">
                    <div class="rec-scroll-card-name">${product.name}</div>
                    <div class="rec-scroll-card-price">${product.price.toLocaleString('ru-RU')} ₽</div>
                    <button class="details-open-btn rec-scroll-card-btn" data-product-name="${product.name}">Подробнее</button>
                </div>
            </div>
        `;
    }
    renderError() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="no-recommendations">
                <p>Не удалось загрузить рекомендации</p>
            </div>
        `;
    }
    initScrollArrows() {
        document.querySelectorAll('.rec-scroll-btn').forEach(btn => {
            btn.removeEventListener('click', this._boundScrollHandler);
            btn.addEventListener('click', this._boundScrollHandler);
        });
    }
}

class SimilarProducts {
    constructor(containerId, productId) {
        this.container = document.getElementById(containerId);
        this.productId = productId;
    }
    async fetch() {
        try {
            const response = await fetch(`${API_URL}/recommendations/similar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: this.productId,
                    n: 6
                })
            });
            if (!response.ok) {
                throw new Error('Ошибка загрузки похожих товаров');
            }
            const similar = await response.json();
            this.render(similar);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }
    render(products) {
        if (!this.container) return;
        const html = `
            <div class="similar-products-section">
                <h4>Похожие товары</h4>
                <div class="similar-products-grid">
                    ${products.map(product => this.createProductCard(product)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
    }
    createProductCard(product) {
        return `
            <div class="similar-product-item" data-product-name="${product.name}">
                <img src="${product.image}" alt="${product.name}">
                <div class="similar-product-item-name">${product.name}</div>
                <div class="similar-product-item-price">${product.price} руб</div>
            </div>
        `;
    }
}

class PopularProducts {
    constructor(containerId, categoryId = null) {
        this.container = document.getElementById(containerId);
        this.categoryId = categoryId;
    }
    async fetch() {
        try {
            let url = `${API_URL}/recommendations/popular?n=10`;
            if (this.categoryId) {
                url += `&category_id=${this.categoryId}`;
            }
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Ошибка загрузки популярных товаров');
            }
            const popular = await response.json();
            this.render(popular);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }
    render(products) {
        if (!this.container) return;
        const html = `
            <div class="rec-scroll-wrapper">
                <div class="rec-scroll-header">
                    <h3>Популярные обои</h3>
                    <div class="rec-scroll-arrows">
                        <button class="rec-scroll-btn rec-scroll-prev" data-track="rec-track-popular">❮</button>
                        <button class="rec-scroll-btn rec-scroll-next" data-track="rec-track-popular">❯</button>
                    </div>
                </div>
                <div class="rec-scroll-track" id="rec-track-popular">
                    ${products.map(product => this.createProductCard(product)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
        this.initScrollArrows();
    }
    createProductCard(product) {
        return `
            <div class="rec-scroll-card" data-product-name="${product.name}" data-product-price="${product.price}" data-product-image="${product.image}" data-product-description="${product.description}">
                <img src="${product.image}" alt="${product.name}">
                <div class="rec-scroll-card-info">
                    <div class="rec-scroll-card-name">${product.name}</div>
                    <div class="rec-scroll-card-price">${product.price.toLocaleString('ru-RU')} ₽</div>
                    <button class="details-open-btn rec-scroll-card-btn" data-product-name="${product.name}">Подробнее</button>
                </div>
            </div>
        `;
    }
    initScrollArrows() {
        document.querySelectorAll('.rec-scroll-btn').forEach(btn => {
            btn.removeEventListener('click', this._boundScrollHandler);
            btn.addEventListener('click', this._boundScrollHandler);
        });
    }
}

async function trackInteraction(userId, productId, interactionType) {
    try {
        await fetch(`${API_URL}/interactions/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                interaction_type: interactionType
            })
        });
    } catch (error) {
        console.error('Ошибка отслеживания взаимодействия:', error);
    }
}

function getUserId() {
    let userId = localStorage.getItem('userId');
    if (!userId) {
        userId = Math.floor(Math.random() * 1000) + 1;
        localStorage.setItem('userId', userId);
    }
    return parseInt(userId);
}

document.addEventListener('DOMContentLoaded', function() {
    const userId = getUserId();

    if (document.getElementById('recommendations-container')) {
        const personalizedRecs = new PersonalizedRecommendations('recommendations-container', userId);
        personalizedRecs.fetch();
    }

    if (document.getElementById('popular-items-container')) {
        const popularProducts = new PopularProducts('popular-items-container');
        popularProducts.fetch();
    }
});
