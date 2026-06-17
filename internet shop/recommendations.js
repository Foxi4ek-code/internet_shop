
class RecommendationClient {
    constructor(apiUrl = 'http://localhost:8000') {
        this.apiUrl = apiUrl;
        this.userId = this.generateUserId();
        this.userHistory = [];
        this.initEventListeners();
    }

    generateUserId() {
        let userId = localStorage.getItem('userId');
        if (!userId) {
            userId = Math.floor(Math.random() * 1000) + 1;
            localStorage.setItem('userId', userId);
        }
        return parseInt(userId);
    }

    initEventListeners() {
                document.addEventListener('click', (e) => {
            const productCard = e.target.closest('.product-card');
            if (productCard) {
                const productId = productCard.dataset.productId;
                if (productId) {
                    this.trackInteraction(productId, 'view');
                }
            }
        });

                document.addEventListener('click', (e) => {
            if (e.target.textContent === 'В корзину' || e.target.classList.contains('add-to-cart')) {
                const productCard = e.target.closest('.product-card');
                if (productCard) {
                    const productId = productCard.dataset.productId;
                    if (productId) {
                        this.trackInteraction(productId, 'purchase');
                    }
                }
            }
        });
    }

    async getPersonalizedRecommendations(n = 10) {
        try {
            const response = await fetch(`${this.apiUrl}/recommendations/personalized`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    n: n,
                    user_history: this.userHistory
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Ошибка получения рекомендаций:', error);
            return [];
        }
    }

    async getSimilarItems(productId, n = 6) {
        try {
            const response = await fetch(`${this.apiUrl}/recommendations/similar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: productId,
                    n: n
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Ошибка получения похожих товаров:', error);
            return [];
        }
    }

    async getPopularItems(n = 10) {
        try {
            const response = await fetch(`${this.apiUrl}/recommendations/popular?n=${n}`);

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Ошибка получения популярных товаров:', error);
            return [];
        }
    }

    async trackInteraction(productId, interactionType) {
        try {
                        if (!this.userHistory.includes(productId)) {
                this.userHistory.push(productId);
            }

                        fetch(`${this.apiUrl}/interactions/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    product_id: productId,
                    interaction_type: interactionType
                })
            }).catch(error => console.error('Ошибка отслеживания взаимодействия:', error));

        } catch (error) {
            console.error('Ошибка при отслеживании взаимодействия:', error);
        }
    }

    async getUserHistory() {
        try {
            const response = await fetch(`${this.apiUrl}/user/${this.userId}/history`);

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Ошибка получения истории:', error);
            return { user_id: this.userId, history: [], total_interactions: 0 };
        }
    }

    async displayRecommendations(containerId = 'recommendations-container', title = 'Рекомендовано для вас') {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Контейнер ${containerId} не найден`);
                return;
            }

            container.innerHTML = '<div class="loading">Загрузка рекомендаций...</div>';

            const recommendations = await this.getPersonalizedRecommendations(10);

            if (recommendations.length === 0) {
                container.innerHTML = '<div class="no-recommendations">Рекомендаций не найдено</div>';
                return;
            }

            const trackId = 'rec-track-' + containerId;
            let html = `
                <div class="rec-scroll-wrapper">
                    <div class="rec-scroll-header">
                        <h3>${title}</h3>
                        <div class="rec-scroll-arrows">
                            <button class="rec-scroll-btn rec-scroll-prev" data-track="${trackId}">❮</button>
                            <button class="rec-scroll-btn rec-scroll-next" data-track="${trackId}">❯</button>
                        </div>
                    </div>
                    <div class="rec-scroll-track" id="${trackId}">
            `;

            recommendations.forEach(product => {
                html += `
                    <div class="rec-scroll-card" data-product-name="${product.name}" data-product-price="${product.price}" data-product-image="${product.image}" data-product-description="${product.description}">
                        <img src="${product.image}" alt="${product.name}">
                        <div class="rec-scroll-card-info">
                            <div class="rec-scroll-card-name">${product.name}</div>
                            <div class="rec-scroll-card-price">${product.price.toLocaleString('ru-RU')} ₽</div>
                            <button class="details-open-btn rec-scroll-card-btn" data-product-name="${product.name}">Подробнее</button>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
            container.innerHTML = html;

                        this.initScrollArrows();

        } catch (error) {
            console.error('Ошибка отображения рекомендаций:', error);
        }
    }

    async displaySimilarItems(productId, containerId = 'similar-items-container', title = 'Похожие товары') {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Контейнер ${containerId} не найден`);
                return;
            }

            container.innerHTML = '<div class="loading">Загрузка похожих товаров...</div>';

            const similarItems = await this.getSimilarItems(productId, 6);

            if (similarItems.length === 0) {
                container.innerHTML = '<div class="no-recommendations">Похожих товаров не найдено</div>';
                return;
            }

            const trackId = 'rec-track-' + containerId;
            let html = `
                <div class="rec-scroll-wrapper">
                    <div class="rec-scroll-header">
                        <h3>${title}</h3>
                        <div class="rec-scroll-arrows">
                            <button class="rec-scroll-btn rec-scroll-prev" data-track="${trackId}">❮</button>
                            <button class="rec-scroll-btn rec-scroll-next" data-track="${trackId}">❯</button>
                        </div>
                    </div>
                    <div class="rec-scroll-track" id="${trackId}">
            `;

            similarItems.forEach(product => {
                html += `
                    <div class="rec-scroll-card" data-product-name="${product.name}" data-product-price="${product.price}" data-product-image="${product.image}" data-product-description="${product.description}">
                        <img src="${product.image}" alt="${product.name}">
                        <div class="rec-scroll-card-info">
                            <div class="rec-scroll-card-name">${product.name}</div>
                            <div class="rec-scroll-card-price">${product.price.toLocaleString('ru-RU')} ₽</div>
                            <button class="details-open-btn rec-scroll-card-btn" data-product-name="${product.name}">Подробнее</button>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
            container.innerHTML = html;

            this.initScrollArrows();

        } catch (error) {
            console.error('Ошибка отображения похожих товаров:', error);
        }
    }

    async displayPopularItems(containerId = 'popular-items-container', title = 'Популярные товары') {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Контейнер ${containerId} не найден`);
                return;
            }

            container.innerHTML = '<div class="loading">Загрузка популярных товаров...</div>';

            const popularItems = await this.getPopularItems(10);

            if (popularItems.length === 0) {
                container.innerHTML = '<div class="no-recommendations">Популярных товаров не найдено</div>';
                return;
            }

            const trackId = 'rec-track-' + containerId;
            let html = `
                <div class="rec-scroll-wrapper">
                    <div class="rec-scroll-header">
                        <h3>${title}</h3>
                        <div class="rec-scroll-arrows">
                            <button class="rec-scroll-btn rec-scroll-prev" data-track="${trackId}">❮</button>
                            <button class="rec-scroll-btn rec-scroll-next" data-track="${trackId}">❯</button>
                        </div>
                    </div>
                    <div class="rec-scroll-track" id="${trackId}">
            `;

            popularItems.forEach(product => {
                html += `
                    <div class="rec-scroll-card" data-product-name="${product.name}" data-product-price="${product.price}" data-product-image="${product.image}" data-product-description="${product.description}">
                        <img src="${product.image}" alt="${product.name}">
                        <div class="rec-scroll-card-info">
                            <div class="rec-scroll-card-name">${product.name}</div>
                            <div class="rec-scroll-card-price">${product.price.toLocaleString('ru-RU')} ₽</div>
                            <button class="details-open-btn rec-scroll-card-btn" data-product-name="${product.name}">Подробнее</button>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
            container.innerHTML = html;

            this.initScrollArrows();

        } catch (error) {
            console.error('Ошибка отображения популярных товаров:', error);
        }
    }

    initScrollArrows() {
        if (!this._boundScrollHandler) {
            this._boundScrollHandler = (e) => {
                const trackId = e.currentTarget.dataset.track;
                const track = document.getElementById(trackId);
                if (!track) return;

                const isNext = e.currentTarget.classList.contains('rec-scroll-next');
                const card = track.querySelector('.rec-scroll-card');
                const scrollAmount = card ? card.offsetWidth + 20 : 300;

                track.scrollBy({
                    left: isNext ? scrollAmount : -scrollAmount,
                    behavior: 'smooth'
                });
            };
        }
        document.querySelectorAll('.rec-scroll-btn').forEach(btn => {
            btn.removeEventListener('click', this._boundScrollHandler);
            btn.addEventListener('click', this._boundScrollHandler);
        });
    }
}

let recommendationClient;

document.addEventListener('DOMContentLoaded', () => {
    recommendationClient = new RecommendationClient('http://localhost:8000');
});
