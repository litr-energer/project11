
const API_BASE_URL = window.location.origin; // Используем текущий origin

const state = {
  products: [],
  cart: JSON.parse(localStorage.getItem('kv_cart')||'{}'),
  query: "",
  category: "all",
  sort: "popular",
  marketListings: [],
  accountListings: [],
  reviews: [],
  user: JSON.parse(localStorage.getItem('kv_user')||'null'),
  favorites: JSON.parse(localStorage.getItem('kv_favs')||'[]'),
  currentPaymentMethod: 'card-visa',
  apiAvailable: false
};

const el = selector => document.querySelector(selector);
const els = selector => Array.from(document.querySelectorAll(selector));

function formatPrice(p){
  return (p === 0) ? "Free" : `${p.toLocaleString('ru-RU')} ₽`;
}

/* API методы с улучшенной обработкой ошибок */
async function apiFetch(endpoint, options = {}) {
  try {
    const url = `${API_BASE_URL}/api${endpoint}`;
    
    const headers = {
      'Accept': 'application/json',
      ...options.headers
    };
    
    // Добавляем Content-Type только если есть тело запроса
    if (options.body && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
    
    // Добавляем токен авторизации если есть
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    console.log(`API Request: ${options.method || 'GET'} ${url}`);
    
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include'
    });
    
    // Если ответ не OK
    if (!response.ok) {
      let errorMsg = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch (e) {
        // Если не JSON, читаем как текст
        const text = await response.text();
        if (text) errorMsg = text;
      }
      
      throw new Error(errorMsg);
    }
    
    // Проверяем тип контента
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
    
  } catch (error) {
    console.error('API fetch error:', error);
    
    // Показываем уведомление только для критических ошибок
    if (!error.message.includes('Failed to fetch') && !error.message.includes('NetworkError')) {
      showToast(`Ошибка API: ${error.message}`, 3000);
    }
    
    throw error;
  }
}

/* Проверка состояния API */
async function checkAPIStatus() {
  try {
    console.log('Checking API status...');
    
    // Пробуем несколько endpoints
    const endpoints = [
      '/health',
      '/api/products/',
      '/api/info'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (response.ok) {
          console.log(`✓ ${endpoint} доступен`);
          state.apiAvailable = true;
          return true;
        }
      } catch (e) {
        console.log(`✗ ${endpoint} недоступен:`, e.message);
      }
    }
    
    // Если ничего не работает
    state.apiAvailable = false;
    return false;
    
  } catch (error) {
    console.error('API health check failed:', error);
    state.apiAvailable = false;
    return false;
  }
}

/* Загрузка данных с API с fallback */
async function loadProducts() {
  if (!state.apiAvailable) {
    console.log('API недоступен, используем тестовые данные');
    loadFallbackProducts();
    return;
  }
  
  try {
    console.log('Loading products from API...');
    const data = await apiFetch('/products/?limit=20');
    
    if (Array.isArray(data)) {
      state.products = data.map(product => ({
        id: product.id?.toString() || String(Math.random()),
        title: product.title || 'Без названия',
        category: product.category || 'other',
        price: parseFloat(product.price) || 0,
        thumb: product.image_url || getDefaultImage(),
        tag: product.category || 'Продукт',
        desc: product.description || 'Описание отсутствует'
      }));
      
      console.log(`Loaded ${state.products.length} products from API`);
      renderProducts();
    } else {
      console.warn('Invalid products data format, using fallback');
      loadFallbackProducts();
    }
  } catch (error) {
    console.error('Failed to load products from API:', error);
    loadFallbackProducts();
  }
}

async function loadReviews() {
  if (!state.apiAvailable) {
    loadFallbackReviews();
    return;
  }
  
  try {
    const data = await apiFetch('/reviews/?limit=10');
    
    if (Array.isArray(data)) {
      state.reviews = data.map(review => ({
        id: review.id,
        name: `Пользователь ${review.user_id || 'Аноним'}`,
        text: review.comment || review.title || 'Без текста',
        rating: review.rating || 5
      }));
      
      console.log(`Loaded ${state.reviews.length} reviews from API`);
      renderReviews();
    } else {
      loadFallbackReviews();
    }
  } catch (error) {
    console.error('Failed to load reviews:', error);
    loadFallbackReviews();
  }
}

async function loadMarketplace() {
  if (!state.apiAvailable) {
    loadFallbackMarketplace();
    return;
  }
  
  try {
    const data = await apiFetch('/listings/?limit=5&status=active');
    
    if (Array.isArray(data)) {
      state.marketListings = data.map(listing => ({
        id: listing.id?.toString() || String(Math.random()),
        title: listing.title || 'Без названия',
        game: listing.game_topic || 'Unknown',
        price: parseFloat(listing.price) || 0,
        thumb: listing.image_url || getDefaultImage(),
        seller: `Продавец ${listing.user_id || 'Аноним'}`
      }));
      
      console.log(`Loaded ${state.marketListings.length} listings from API`);
      renderMarketplace();
    } else {
      loadFallbackMarketplace();
    }
  } catch (error) {
    console.error('Failed to load marketplace:', error);
    loadFallbackMarketplace();
  }
}

async function loadAuthorListings() {
  if (!state.apiAvailable) {
    loadFallbackAuthorListings();
    return;
  }
  
  try {
    const data = await apiFetch('/author-listings/?limit=5&status=active');
    
    if (Array.isArray(data)) {
      state.accountListings = data.map(listing => ({
        id: listing.id?.toString() || String(Math.random()),
        title: listing.title || 'Без названия',
        games: listing.topics_games || listing.category || 'General',
        price: parseFloat(listing.price) || 0,
        thumb: listing.image_url || getDefaultImage(),
        seller: `Автор ${listing.user_id || 'Аноним'}`
      }));
      
      console.log(`Loaded ${state.accountListings.length} author listings from API`);
      renderAccountsMarketplace();
    } else {
      loadFallbackAuthorListings();
    }
  } catch (error) {
    console.error('Failed to load author listings:', error);
    loadFallbackAuthorListings();
  }
}

/* Fallback данные */
function loadFallbackProducts() {
  state.products = [
    {
      id: "1",
      title: "Dota 2 — Полный гид и тактики (eBook)",
      category: "guides",
      price: 499,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
      tag: "Гид",
      desc: "Подробные тактики, сборки и разбор ролей — eBook для игроков всех уровней."
    },
    {
      id: "2",
      title: "CS:GO — Тактики, карты и экономия (eBook)",
      category: "guides",
      price: 399,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
      tag: "Гайд",
      desc: "Практические руководства по картам, экономике и стрельбе."
    },
    {
      id: "3",
      title: "The Witcher 3 — Лор, квесты и билд-гайд (eBook)",
      category: "rpg",
      price: 499,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg",
      tag: "Лор",
      desc: "Подробный разбор сюжета, заданий и советов по построению персонажа."
    },
    {
      id: "4",
      title: "Elden Ring — Тактики боссов и билды (eBook)",
      category: "rpg",
      price: 399,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/1248130/header.jpg",
      tag: "Гайд",
      desc: "Разбор механик боссов, оптимальные билды и маршруты по локациям."
    }
  ];
  
  console.log(`Loaded ${state.products.length} fallback products`);
  renderProducts();
}

function loadFallbackReviews() {
  state.reviews = [
    { id: 1, name: "Алексей", text: "Отличный сервис! Быстрая доставка.", rating: 5 },
    { id: 2, name: "Мария", text: "Качественные материалы, много полезных схем.", rating: 5 },
    { id: 3, name: "Иван", text: "Удобный интерфейс магазина.", rating: 4 },
    { id: 4, name: "Ольга", text: "Хорошие цены на тематические сборники.", rating: 5 },
    { id: 5, name: "Дмитрий", text: "Быстро получил ссылку после оплаты.", rating: 5 }
  ];
  
  renderReviews();
}

function loadFallbackMarketplace() {
  state.marketListings = [
    {
      id: "lst-1",
      title: "AWP | Истории коллекционеров (eBook)",
      game: "CS:GO",
      price: 399,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
      seller: "Игрок123"
    },
    {
      id: "lst-2",
      title: "Rare Courier — Истории предметов (eBook)",
      game: "Dota 2",
      price: 349,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
      seller: "MarketPro"
    }
  ];
  
  renderMarketplace();
}

function loadFallbackAuthorListings() {
  state.accountListings = [
    {
      id: "acc-1",
      title: "Авторское издание: Истории CS:GO",
      games: "CS:GO",
      price: 249,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
      seller: "MarketUser"
    },
    {
      id: "acc-2",
      title: "Авторское издание: Курьеры Dota 2",
      games: "Dota 2",
      price: 299,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
      seller: "SellerPro"
    }
  ];
  
  renderAccountsMarketplace();
}

/* Вспомогательные функции */
function getDefaultImage() {
  return 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
      <rect width="400" height="200" fill="#2d2d2d"/>
      <text x="200" y="100" font-family="Arial" font-size="20" fill="#888" text-anchor="middle">No Image</text>
    </svg>
  `);
}

/* Инициализация приложения */
async function initApp() {
  console.log('Initializing application...');
  
  try {
    // 1. Проверяем доступность API
    const isApiAvailable = await checkAPIStatus();
    
    if (isApiAvailable) {
      showToast('Подключаемся к серверу...', 1500);
      console.log('API доступен, загружаем данные...');
    } else {
      showToast('Сервер недоступен. Используем демо-данные.', 3000);
      console.log('API недоступен, используем fallback данные');
    }
    
    // 2. Проверяем авторизацию
    await checkAuthStatus();
    
    // 3. Загружаем данные
    if (isApiAvailable) {
      // Пробуем загрузить с API
      try {
        await Promise.all([
          loadProducts(),
          loadReviews(),
          loadMarketplace(),
          loadAuthorListings()
        ]);
        showToast('Данные загружены', 1500);
      } catch (error) {
        console.error('Error loading from API, using fallback:', error);
        // Если не удалось загрузить с API, используем fallback
        loadFallbackProducts();
        loadFallbackReviews();
        loadFallbackMarketplace();
        loadFallbackAuthorListings();
        showToast('Используем демо-данные', 2000);
      }
    } else {
      // Используем только fallback
      loadFallbackProducts();
      loadFallbackReviews();
      loadFallbackMarketplace();
      loadFallbackAuthorListings();
    }
    
    // 4. Инициализируем UI
    initUI();
    
    console.log('Application initialized successfully');
    
  } catch (error) {
    console.error('Failed to initialize app:', error);
    
    // Минимальная функциональность даже при ошибках
    loadFallbackProducts();
    loadFallbackReviews();
    initUI();
    
    showToast('Приложение загружено в режиме демо', 3000);
  }
}

/* Проверка статуса авторизации */
async function checkAuthStatus() {
  const token = localStorage.getItem('access_token');
  const userData = localStorage.getItem('kv_user');
  
  if (token && userData) {
    try {
      if (state.apiAvailable) {
        const response = await apiFetch('/auth/me');
        if (response) {
          state.user = response;
        }
      } else {
        state.user = JSON.parse(userData);
      }
    } catch (error) {
      console.log('Token check failed, using local data:', error);
      state.user = JSON.parse(userData);
    }
  }
  
  renderAuthArea();
}

/* Рендеринг продуктов */
function renderProducts() {
  const container = el('#products');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (state.products.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <h3>Товары не найдены</h3>
        <p>Попробуйте изменить фильтры или поисковый запрос</p>
      </div>
    `;
    return;
  }
  
  let list = [...state.products];
  
  // Фильтрация
  if (state.category !== 'all') {
    list = list.filter(p => p.category === state.category);
  }
  
  if (state.query) {
    const query = state.query.toLowerCase();
    list = list.filter(p => 
      p.title.toLowerCase().includes(query) ||
      p.desc.toLowerCase().includes(query) ||
      p.tag.toLowerCase().includes(query)
    );
  }
  
  // Сортировка
  if (state.sort === 'price-asc') list.sort((a,b) => a.price - b.price);
  if (state.sort === 'price-desc') list.sort((a,b) => b.price - a.price);
  if (state.sort === 'popular') list.sort((a,b) => a.title.localeCompare(b.title));
  
  // Рендеринг
  list.forEach(p => {
    const isFav = state.favorites.includes(p.id);
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.pid = p.id;
    card.innerHTML = `
      <div class="media">
        <img src="${p.thumb}" alt="${p.title}" loading="lazy" onerror="this.src='${getDefaultImage()}'">
      </div>
      <div class="card-content">
        <h3>${p.title}</h3>
        <div class="meta">
          <span class="tag-pill">${p.tag}</span>
          <span class="price">${formatPrice(p.price)}</span>
        </div>
        <p class="description">${p.desc}</p>
      </div>
      <div class="card-actions">
        <div class="action-group">
          <button class="btn add-to-cart" data-id="${p.id}">Добавить</button>
          <button class="btn ghost buy-now" data-id="${p.id}">Купить</button>
        </div>
        <button class="btn ghost favorite-btn" data-id="${p.id}" aria-label="Избранное">
          ${isFav ? '★' : '☆'}
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

/* Рендеринг отзывов */
function renderReviews() {
  const wrap = el('#reviewsGrid');
  if (!wrap) return;
  
  wrap.innerHTML = '';
  
  state.reviews.forEach(r => {
    const node = document.createElement('div');
    node.className = 'card review-card';
    node.innerHTML = `
      <div class="review-header">
        <div class="profile-avatar">${r.name[0].toUpperCase()}</div>
        <div>
          <strong>${r.name}</strong>
          <div class="stars">${'★'.repeat(r.rating)}${'☆'.repeat(5-r.rating)}</div>
        </div>
      </div>
      <div class="review-text">${r.text}</div>
    `;
    wrap.appendChild(node);
  });
}

/* Рендеринг маркетплейса */
function renderMarketplace() {
  const wrap = el('#marketGrid');
  if (!wrap) return;
  
  wrap.innerHTML = '';
  
  if (state.marketListings.length === 0) {
    wrap.innerHTML = '<div class="empty-state">Объявления отсутствуют</div>';
    return;
  }
  
  state.marketListings.forEach(l => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="media">
        <img src="${l.thumb}" alt="${l.title}" loading="lazy">
      </div>
      <div class="card-content">
        <h3>${l.title}</h3>
        <div class="meta">
          <span class="tag-pill">#${l.game}</span>
          <span class="price">${formatPrice(l.price)}</span>
        </div>
        <p>Продавец: ${l.seller}</p>
      </div>
      <div class="card-actions">
        <button class="btn primary buy-listing" data-id="${l.id}">Купить</button>
        <button class="btn ghost" data-id="${l.id}">В корзину</button>
      </div>
    `;
    wrap.appendChild(card);
  });
}

/* Рендеринг авторских объявлений */
function renderAccountsMarketplace() {
  const wrap = el('#accMarketGrid');
  if (!wrap) return;
  
  wrap.innerHTML = '';
  
  if (state.accountListings.length === 0) {
    wrap.innerHTML = '<div class="empty-state">Авторские издания отсутствуют</div>';
    return;
  }
  
  state.accountListings.forEach(l => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="media">
        <img src="${l.thumb}" alt="${l.title}" loading="lazy">
      </div>
      <div class="card-content">
        <h3>${l.title}</h3>
        <div class="meta">
          <span class="tag-pill">${l.games}</span>
          <span class="price">${formatPrice(l.price)}</span>
        </div>
        <p>Автор: ${l.seller}</p>
      </div>
      <div class="card-actions">
        <button class="btn primary buy-acc" data-id="${l.id}">Купить</button>
        <button class="btn ghost add-acc" data-id="${l.id}">В корзину</button>
      </div>
    `;
    wrap.appendChild(card);
  });
}

/* UI инициализация */
function initUI() {
  console.log('Initializing UI...');
  
  // Инициализация поиска
  const searchInput = el('#search');
  if (searchInput) {
    let searchTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.query = e.target.value.trim();
        renderProducts();
      }, 300);
    });
  }
  
  // Инициализация категорий
  const categoryButtons = els('.category-chip');
  categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.category = btn.dataset.category || 'all';
      renderProducts();
    });
  });
  
  // Инициализация сортировки
  const sortButtons = els('.sort-chip');
  sortButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      sortButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.sort = btn.dataset.sort || 'popular';
      renderProducts();
    });
  });
  
  // Кнопка корзины
  const cartBtn = el('#cartBtn');
  if (cartBtn) {
    cartBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = '/cart.html';
    });
  }
  
  // Кнопка авторизации
  const authBtn = el('#authBtn');
  if (authBtn) {
    authBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = '/auth.html';
    });
  }
  
  // Обновляем счетчик корзины
  updateCartUI();
  
  console.log('UI initialized');
}

/* Обновление интерфейса корзины */
function updateCartUI() {
  const cartCountEl = el('#cartCount');
  if (cartCountEl) {
    const totalItems = Object.values(state.cart).reduce((sum, item) => sum + (item.qty || 0), 0);
    cartCountEl.textContent = totalItems;
    cartCountEl.style.display = totalItems > 0 ? 'block' : 'none';
  }
}

/* Уведомления */
function showToast(message, duration = 3000) {
  // Создаем или находим контейнер для тостов
  let toastContainer = el('#toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
    `;
    document.body.appendChild(toastContainer);
  }
  
  // Создаем тост
  const toast = document.createElement('div');
  toast.className = 'toast-message';
  toast.style.cssText = `
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: slideIn 0.3s ease;
    max-width: 300px;
  `;
  
  toast.textContent = message;
  toastContainer.appendChild(toast);
  
  // Удаляем через указанное время
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, duration);
}

// Добавляем CSS анимации
if (!document.querySelector('#toast-animations')) {
  const style = document.createElement('style');
  style.id = 'toast-animations';
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
}

/* Базовые функции для работы с корзиной */
function addToCart(id, quantity = 1) {
  const product = state.products.find(p => p.id === id) ||
                  state.marketListings.find(p => p.id === id) ||
                  state.accountListings.find(p => p.id === id);
  
  if (!product) {
    showToast('Товар не найден');
    return;
  }
  
  state.cart[id] = state.cart[id] || { ...product, qty: 0 };
  state.cart[id].qty += quantity;
  
  updateCartUI();
  showToast(`Добавлено: ${product.title}`);
  
  // Сохраняем в localStorage
  localStorage.setItem('kv_cart', JSON.stringify(state.cart));
}

/* Запуск приложения */
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, starting app...');
  
  // Запускаем с задержкой чтобы DOM полностью загрузился
  setTimeout(() => {
    initApp().catch(error => {
      console.error('Critical error during app initialization:', error);
      
      // Минимальная функциональность даже при критических ошибках
      loadFallbackProducts();
      initUI();
      showToast('Приложение загружено в автономном режиме', 3000);
    });
  }, 100);
});

// Экспортируем функции для использования в других файлах
window.appState = state;
window.apiFetch = apiFetch;
window.showToast = showToast;
window.addToCart = addToCart;

console.log('App script loaded');
