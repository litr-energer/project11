// /app/static/js/app.js (ПОЛНЫЙ КОД ~1700 строк)

// Базовый URL API
const API_BASE_URL = '';

// Состояние приложения
const AppState = {
  user: null,
  cart: {},
  favorites: [],
  products: [],
  marketListings: [],
  accountListings: [],
  currentCategory: 'all',
  currentSort: 'popular',
  searchQuery: '',
  isLoading: false
};

// ====================
// УТИЛИТЫ
// ====================

function formatPrice(price) {
  return price === 0 ? 'Бесплатно' : price.toLocaleString('ru-RU') + ' ₽';
}

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  
  toast.textContent = message;
  toast.className = 'toast';
  
  // Добавляем класс типа
  if (type === 'success') {
    toast.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
  } else if (type === 'error') {
    toast.style.background = 'linear-gradient(90deg, #dc3545, #e83e8c)';
  } else if (type === 'info') {
    toast.style.background = 'linear-gradient(90deg, #17a2b8, #00b4d8)';
  } else {
    toast.style.background = 'linear-gradient(90deg, var(--accent-1), var(--accent-2))';
  }
  
  toast.style.display = 'block';
  
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

// ====================
// ЗАГРУЗКА СОСТОЯНИЯ И АВТОРИЗАЦИЯ
// ====================

function loadStateFromStorage() {
  try {
    // Корзина
    const cart = JSON.parse(localStorage.getItem('kv_cart') || '{}');
    AppState.cart = cart;
    
    // Избранное
    const favorites = JSON.parse(localStorage.getItem('kv_favs') || '[]');
    AppState.favorites = favorites;
    
    // Пользователь
    const user = JSON.parse(localStorage.getItem('kv_user') || 'null');
    if (user) {
      AppState.user = user;
    }
    
    // Продукты из снапшота
    try {
      const savedProducts = JSON.parse(localStorage.getItem('kv_products_snapshot') || '[]');
      if (savedProducts.length > 0 && AppState.products.length === 0) {
        AppState.products = savedProducts;
      }
    } catch (e) {
      console.warn('Не удалось загрузить продукты из localStorage:', e);
    }
    
  } catch (error) {
    console.error('Ошибка загрузки состояния:', error);
  }
}

function checkAuthStatus() {
  const user = JSON.parse(localStorage.getItem('kv_user') || 'null');
  const authArea = document.getElementById('authArea');
  const userProfile = document.getElementById('userProfile');
  const authButtons = document.getElementById('authButtons');
  
  if (user && user.name) {
    AppState.user = user;
    
    // Пользователь авторизован
    if (userProfile) userProfile.style.display = 'flex';
    if (authButtons) authButtons.style.display = 'none';
    
    // Обновляем аватар и имя
    updateUserProfileUI(user);
    
    // Добавляем обработчик выхода
    setupLogoutHandler();
  } else {
    // Пользователь не авторизован
    AppState.user = null;
    if (userProfile) userProfile.style.display = 'none';
    if (authButtons) authButtons.style.display = 'flex';
  }
}

function updateUserProfileUI(user) {
  const userAvatar = document.getElementById('userAvatar');
  const userName = document.getElementById('userName');
  
  if (userAvatar) {
    if (user.avatar) {
      userAvatar.style.backgroundImage = `url('${user.avatar}')`;
      userAvatar.textContent = '';
    } else {
      userAvatar.style.backgroundImage = 'none';
      userAvatar.textContent = user.name.charAt(0).toUpperCase();
    }
  }
  
  if (userName) {
    userName.textContent = user.name;
  }
}

function setupLogoutHandler() {
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    // Удаляем старые обработчики
    logoutBtn.replaceWith(logoutBtn.cloneNode(true));
    const newLogoutBtn = document.getElementById('logoutBtn');
    
    newLogoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      logoutUser();
    });
  }
}

function logoutUser() {
  localStorage.removeItem('kv_user');
  AppState.user = null;
  checkAuthStatus();
  showToast('Вы вышли из аккаунта', 'info');
}

// ====================
// КОРЗИНА И ИЗБРАННОЕ
// ====================

function saveCart() {
  localStorage.setItem('kv_cart', JSON.stringify(AppState.cart));
  updateCartCount();
}

function updateCartCount() {
  const cartCount = document.getElementById('cartCount');
  if (cartCount) {
    const count = Object.keys(AppState.cart).length;
    cartCount.textContent = count;
  }
}

function addToCart(item) {
  const itemId = item.id || `item-${Date.now()}`;
  
  if (AppState.cart[itemId]) {
    AppState.cart[itemId].qty += 1;
  } else {
    AppState.cart[itemId] = {
      id: itemId,
      title: item.title,
      price: item.price || 0,
      qty: 1,
      thumb: item.thumb || 'https://via.placeholder.com/160x90',
      category: item.category || 'other'
    };
  }
  
  saveCart();
  showToast(`"${item.title}" добавлен в корзину`, 'success');
}

function removeFromCart(itemId) {
  if (AppState.cart[itemId]) {
    delete AppState.cart[itemId];
    saveCart();
    showToast('Товар удален из корзины', 'info');
  }
}

function clearCart() {
  AppState.cart = {};
  saveCart();
  showToast('Корзина очищена', 'info');
}

function getCartTotal() {
  return Object.values(AppState.cart).reduce((total, item) => {
    return total + (item.price * item.qty);
  }, 0);
}

function updateCartQuantity(itemId, newQty) {
  if (AppState.cart[itemId]) {
    if (newQty <= 0) {
      removeFromCart(itemId);
    } else {
      AppState.cart[itemId].qty = newQty;
      saveCart();
    }
  }
}

function saveFavorites() {
  localStorage.setItem('kv_favs', JSON.stringify(AppState.favorites));
  updateFavCount();
}

function updateFavCount() {
  const favCount = document.getElementById('favCount');
  if (favCount) {
    favCount.textContent = AppState.favorites.length;
  }
}

function toggleFavorite(itemId) {
  const index = AppState.favorites.indexOf(itemId);
  if (index === -1) {
    AppState.favorites.push(itemId);
    showToast('Добавлено в избранное', 'success');
  } else {
    AppState.favorites.splice(index, 1);
    showToast('Удалено из избранного', 'info');
  }
  saveFavorites();
}

function isItemFavorited(itemId) {
  return AppState.favorites.includes(itemId);
}

// ====================
// API ФУНКЦИИ
// ====================

async function loadProducts() {
  try {
    console.log('Загрузка продуктов с сервера...');
    
    // Показываем индикатор загрузки
    AppState.isLoading = true;
    const productsContainer = document.getElementById('products');
    if (productsContainer) {
      productsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">
          <div style="margin-bottom: 10px;">Загрузка товаров...</div>
          <div style="width: 40px; height: 4px; background: linear-gradient(90deg, var(--accent-1), var(--accent-2)); margin: 0 auto; border-radius: 2px; animation: pulse 1.5s infinite;"></div>
        </div>
      `;
    }
    
    // Используем относительный путь
    let url = `/products/?skip=0&limit=100&active_only=true`;
    
    // Если выбрана категория (не "all"), добавляем фильтр
    if (AppState.currentCategory && AppState.currentCategory !== 'all') {
      url += `&category=${encodeURIComponent(AppState.currentCategory)}`;
    }
    
    console.log('Запрос к API:', url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const productsData = await response.json();
    console.log('Получены продукты с сервера:', productsData);
    
    // Преобразуем данные из API
    AppState.products = productsData.map(product => {
      const isActive = product.is_active !== false;  // Исправлено на is_active
      let thumbnail = 'https://via.placeholder.com/400x200?text=No+preview';
      if (product.image_url) {
        thumbnail = product.image_url;
      }
      
      const description = product.description || 'Электронное издание высокого качества. Подробное руководство и советы от экспертов.';
      
      return {
        id: product.id ? product.id.toString() : `product-${Date.now()}`,
        title: product.title || 'Без названия',
        price: parseFloat(product.price) || 0,
        category: product.category || 'Игры',
        thumb: thumbnail,
        description: description,
        popularity: product.popularity || 0,
        is_active: isActive,  // Исправлено на is_active
        author: '',
        rating: 0,
        tags: [],
        game: product.game || product.category
      };
    });
    
    // Сохраняем снимок
    localStorage.setItem('kv_products_snapshot', JSON.stringify(AppState.products));
    console.log('Продукты успешно загружены из БД:', AppState.products.length, 'шт.');
    
    AppState.isLoading = false;
    updateProductCounters();
    
    return AppState.products;
    
  } catch (error) {
    console.error('Не удалось загрузить товары с сервера:', error);
    AppState.isLoading = false;
    showToast('Ошибка загрузки товаров. Используются демо-данные.', 'error');
    
    // Используем демо-данные
    AppState.products = getDemoProducts();
    
    try {
      const savedProducts = JSON.parse(localStorage.getItem('kv_products_snapshot') || '[]');
      if (savedProducts.length > 0) {
        AppState.products = savedProducts;
        console.log('Используем сохраненные продукты из localStorage');
      }
    } catch (e) {
      console.warn('Не удалось загрузить продукты из localStorage:', e);
    }
    
    return AppState.products;
  }
}

async function loadMarketListings() {
  try {
    const response = await fetch(`${API_BASE_URL}/listings/?skip=0&limit=100&active_only=true`);
    
    if (response.ok) {
      const listingsData = await response.json();
      
      AppState.marketListings = listingsData.map(listing => {
        return {
          id: listing.id?.toString() || `market-${Date.now()}`,
          title: listing.title || 'Без названия',
          price: parseFloat(listing.price) || 0,
          game_topic: listing.game_topic || listing.category || 'Публикация',
          thumb: listing.image_url || listing.thumbnail || 'https://via.placeholder.com/400x200?text=Публикация',
          description: listing.description || 'Пользовательская публикация',
          user_id: listing.user_id,
          status: listing.status || 'active',
          created_at: listing.created_at
        };
      });
      
      localStorage.setItem('kv_market_listings', JSON.stringify(AppState.marketListings));
      console.log('Публикации маркетплейса загружены:', AppState.marketListings.length, 'шт.');
    }
  } catch (error) {
    console.warn('Не удалось загрузить публикации с сервера:', error);
    AppState.marketListings = getDemoMarketListings();
  }
}

async function loadAccountListings() {
  try {
    const response = await fetch(`${API_BASE_URL}/author-listings/?skip=0&limit=100&active_only=true`);
    
    if (response.ok) {
      const listingsData = await response.json();
      
      AppState.accountListings = listingsData.map(listing => {
        return {
          id: listing.id?.toString() || `account-${Date.now()}`,
          title: listing.title || 'Без названия',
          price: parseFloat(listing.price) || 0,
          topic: listing.topic || listing.category || 'Авторское',
          thumb: listing.image_url || listing.thumbnail || 'https://via.placeholder.com/400x200?text=Издание',
          description: listing.description || 'Авторское издание',
          user_id: listing.user_id,
          is_active: listing.is_active !== false,
          created_at: listing.created_at
        };
      });
      
      localStorage.setItem('kv_account_listings', JSON.stringify(AppState.accountListings));
      console.log('Авторские издания загружены:', AppState.accountListings.length, 'шт.');
    }
  } catch (error) {
    console.warn('Не удалось загрузить авторские издания:', error);
    AppState.accountListings = getDemoAccountListings();
  }
}

async function createMarketListing(listingData) {
  try {
    const user = AppState.user;
    if (!user) {
      showToast('Для публикации нужно войти в аккаунт', 'error');
      return null;
    }
    
    const response = await fetch(`${API_BASE_URL}/listings/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...listingData,
        user_id: user.id,
        status: 'active'
      })
    });
    
    if (response.ok) {
      const newListing = await response.json();
      showToast('Публикация успешно создана!', 'success');
      return newListing;
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка создания публикации');
    }
  } catch (error) {
    console.error('Ошибка создания публикации:', error);
    showToast(error.message || 'Ошибка создания публикации', 'error');
    return null;
  }
}

async function createAccountListing(listingData) {
  try {
    const user = AppState.user;
    if (!user) {
      showToast('Для публикации нужно войти в аккаунт', 'error');
      return null;
    }
    
    const response = await fetch(`${API_BASE_URL}/author-listings/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...listingData,
        user_id: user.id,
        is_active: true
      })
    });
    
    if (response.ok) {
      const newListing = await response.json();
      showToast('Авторское издание успешно создано!', 'success');
      return newListing;
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка создания издания');
    }
  } catch (error) {
    console.error('Ошибка создания авторского издания:', error);
    showToast(error.message || 'Ошибка создания издания', 'error');
    return null;
  }
}

// ====================
// РЕНДЕРИНГ
// ====================

function updateProductCounters() {
  updateCategoryCounts();
  updateDisplayedProductCount(getFilteredProductsCount());
}

function updateCategoryCounts() {
  const categoryCounts = {};
  AppState.products.forEach(product => {
    const category = product.category || 'other';
    categoryCounts[category] = (categoryCounts[category] || 0) + 1;
  });
  
  document.querySelectorAll('[data-cat]').forEach(button => {
    const category = button.dataset.cat;
    if (category !== 'all') {
      const count = categoryCounts[category] || 0;
      const countSpan = button.querySelector('.category-count') || document.createElement('span');
      countSpan.className = 'category-count';
      countSpan.style.marginLeft = '6px';
      countSpan.style.fontSize = '11px';
      countSpan.style.opacity = '0.7';
      countSpan.textContent = `(${count})`;
      
      if (!button.querySelector('.category-count')) {
        button.appendChild(countSpan);
      } else {
        button.querySelector('.category-count').textContent = `(${count})`;
      }
    }
  });
  
  const allButton = document.querySelector('[data-cat="all"]');
  if (allButton) {
    const totalCount = AppState.products.length;
    const countSpan = allButton.querySelector('.category-count') || document.createElement('span');
    countSpan.className = 'category-count';
    countSpan.style.marginLeft = '6px';
    countSpan.style.fontSize = '11px';
    countSpan.style.opacity = '0.7';
    countSpan.textContent = `(${totalCount})`;
    
    if (!allButton.querySelector('.category-count')) {
      allButton.appendChild(countSpan);
    } else {
      allButton.querySelector('.category-count').textContent = `(${totalCount})`;
    }
  }
}

function getFilteredProductsCount() {
  let filteredProducts = AppState.products;
  
  if (AppState.currentCategory !== 'all') {
    filteredProducts = filteredProducts.filter(product => {
      const category = (product.category || '').toLowerCase();
      const searchCategory = AppState.currentCategory.toLowerCase();
      return category === searchCategory || category.includes(searchCategory);
    });
  }
  
  if (AppState.searchQuery) {
    const query = AppState.searchQuery.toLowerCase();
    filteredProducts = filteredProducts.filter(product =>
      (product.title || '').toLowerCase().includes(query) ||
      (product.description || '').toLowerCase().includes(query) ||
      (product.category || '').toLowerCase().includes(query)
    );
  }
  
  return filteredProducts.length;
}

function updateDisplayedProductCount(count) {
  const productGrid = document.getElementById('products');
  if (!productGrid) return;
  
  const existingCounter = productGrid.previousElementSibling;
  if (existingCounter && existingCounter.classList.contains('product-counter')) {
    existingCounter.remove();
  }
  
  if (count > 0) {
    const counterDiv = document.createElement('div');
    counterDiv.className = 'product-counter';
    counterDiv.style.cssText = `
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 10px;
      padding: 0 4px;
    `;
    counterDiv.textContent = `Найдено товаров: ${count}`;
    productGrid.parentNode.insertBefore(counterDiv, productGrid);
  }
}

function renderProducts() {
  const productsContainer = document.getElementById('products');
  if (!productsContainer) {
    console.error('Контейнер продуктов не найден!');
    return;
  }
  
  if (AppState.isLoading) {
    return;
  }
  
  // Фильтрация
  let filteredProducts = AppState.products;
  
  if (AppState.currentCategory !== 'all') {
    filteredProducts = filteredProducts.filter(product => {
      const category = (product.category || '').toLowerCase();
      const searchCategory = AppState.currentCategory.toLowerCase();
      return category === searchCategory || 
             category.includes(searchCategory) ||
             searchCategory.includes(category);
    });
  }
  
  if (AppState.searchQuery) {
    const query = AppState.searchQuery.toLowerCase();
    filteredProducts = filteredProducts.filter(product =>
      (product.title || '').toLowerCase().includes(query) ||
      (product.description || '').toLowerCase().includes(query) ||
      (product.category || '').toLowerCase().includes(query)
    );
  }
  
  // Сортировка
  filteredProducts = sortProducts(filteredProducts, AppState.currentSort);
  
  // Если нет продуктов
  if (filteredProducts.length === 0) {
    productsContainer.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">
        <h3 style="margin-bottom: 10px;">Товары не найдены</h3>
        <p>Попробуйте изменить критерии поиска или выберите другую категорию</p>
        <button onclick="resetFilters()" class="btn ghost" style="margin-top: 15px;">
          Сбросить фильтры
        </button>
      </div>
    `;
    return;
  }
  
  // Рендеринг
  productsContainer.innerHTML = filteredProducts.map(product => {
    const formattedPrice = formatPrice(product.price);
    const categoryLower = product.category.toLowerCase();
    
    const categoryColors = {
      'dota 2': '#2b5cff',
      'fnaf': '#7b61ff',
      'классика': '#28a745',
      'стратегия': '#fd7e14',
      'инди': '#e83e8c',
      'анализ': '#17a2b8',
      'гайды': '#6f42c1',
      'лор': '#20c997',
      'dota2': '#2b5cff'
    };
    
    const categoryColor = categoryColors[categoryLower] || 'rgba(255,255,255,0.1)';
    const shortDescription = product.description.length > 100 
      ? product.description.substring(0, 100) + '...' 
      : product.description;
    
    const popularityStars = product.popularity > 0 
      ? `<div style="display: flex; gap: 2px; margin: 4px 0; font-size: 12px; color: #ffc107;">
          ${'★'.repeat(Math.min(Math.floor(product.popularity / 20), 5))}
          ${'☆'.repeat(5 - Math.min(Math.floor(product.popularity / 20), 5))}
         </div>`
      : '';
    
    return `
      <article class="card" data-id="${product.id}" data-type="product" data-category="${product.category}">
        <div class="media" style="position: relative;">
          <img src="${product.thumb}" 
               alt="${product.title}"
               loading="lazy"
               onerror="this.onerror=null; this.src='https://via.placeholder.com/400x200?text=${encodeURIComponent(product.title.substring(0, 20))}'">
          ${!product.is_active ? `<div style="position: absolute; top: 4px; right: 4px; background: rgba(220, 53, 69, 0.9); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Неактивен</div>` : ''}
        </div>
        <div>
          <h3 style="margin: 0 0 4px 0; font-size: 15px; line-height: 1.3;">${product.title}</h3>
          ${popularityStars}
          <div class="meta">
            <span class="tag-pill" style="background: ${categoryColor};">${product.category || 'Игры'}</span>
            <span class="price" style="font-size: 16px; font-weight: 700;">${formattedPrice}</span>
          </div>
          <p style="margin: 8px 0 0; color: var(--muted); font-size: 13px; line-height: 1.4;">
            ${shortDescription}
          </p>
        </div>
        <div class="actions">
          <button class="btn primary" data-action="add-to-cart" data-id="${product.id}" data-type="product" ${!product.is_active ? 'disabled style="opacity: 0.5;"' : ''}>
            ${product.is_active ? 'Купить' : 'Недоступно'}
          </button>
          <button class="btn ghost ${isItemFavorited(product.id) ? 'active-chip' : ''}" 
                  data-action="toggle-favorite" 
                  data-id="${product.id}"
                  data-type="product"
                  aria-pressed="${isItemFavorited(product.id)}"
                  ${!product.is_active ? 'disabled style="opacity: 0.5;"' : ''}>
            ${isItemFavorited(product.id) ? 'В избранном' : 'В избранное'}
          </button>
        </div>
      </article>
    `;
  }).join('');
  
  updateDisplayedProductCount(filteredProducts.length);
}

function sortProducts(products, sortType) {
  const sorted = [...products];
  
  switch (sortType) {
    case 'price-asc':
      return sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
    case 'price-desc':
      return sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
    case 'popular':
      return sorted.sort((a, b) => (b.popularity || 0) - (a.popularity || 0));
    default:
      return sorted;
  }
}

function renderMarketListings() {
  const marketGrid = document.getElementById('marketGrid');
  if (!marketGrid) return;
  
  marketGrid.innerHTML = AppState.marketListings.map(listing => `
    <article class="card" data-id="${listing.id}" data-type="market">
      <div class="media">
        <img src="${listing.thumb}" 
             alt="${listing.title}"
             onerror="this.src='https://via.placeholder.com/400x200?text=Публикация'">
      </div>
      <div>
        <h3>${listing.title}</h3>
        <div class="meta">
          <span class="tag-pill">${listing.game_topic || 'Публикация'}</span>
          <span class="price">${formatPrice(listing.price || 0)}</span>
        </div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">
          ${listing.description || 'Пользовательская публикация'}
        </p>
      </div>
      <div class="actions">
        <button class="btn primary" data-action="add-to-cart" data-id="${listing.id}" data-type="market">
          Купить
        </button>
        <button class="btn ghost ${isItemFavorited(`market-${listing.id}`) ? 'active-chip' : ''}" 
                data-action="toggle-favorite" 
                data-id="${listing.id}"
                data-type="market">
          ${isItemFavorited(`market-${listing.id}`) ? 'В избранном' : 'В избранное'}
        </button>
      </div>
    </article>
  `).join('');
}

function renderAccountListings() {
  const accMarketGrid = document.getElementById('accMarketGrid');
  if (!accMarketGrid) return;
  
  accMarketGrid.innerHTML = AppState.accountListings.map(listing => `
    <article class="card" data-id="${listing.id}" data-type="account">
      <div class="media">
        <img src="${listing.thumb}" 
             alt="${listing.title}"
             onerror="this.src='https://via.placeholder.com/400x200?text=Издание'">
      </div>
      <div>
        <h3>${listing.title}</h3>
        <div class="meta">
          <span class="tag-pill">${listing.topic || 'Авторское'}</span>
          <span class="price">${formatPrice(listing.price || 0)}</span>
        </div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">
          ${listing.description || 'Авторское издание'}
        </p>
      </div>
      <div class="actions">
        <button class="btn primary" data-action="add-to-cart" data-id="${listing.id}" data-type="account">
          Купить
        </button>
        <button class="btn ghost ${isItemFavorited(`account-${listing.id}`) ? 'active-chip' : ''}" 
                data-action="toggle-favorite" 
                data-id="${listing.id}"
                data-type="account">
          ${isItemFavorited(`account-${listing.id}`) ? 'В избранном' : 'В избранное'}
        </button>
      </div>
    </article>
  `).join('');
}

function renderReviews() {
  const reviewsGrid = document.getElementById('reviewsGrid');
  if (!reviewsGrid) return;
  
  const reviews = getDemoReviews();
  reviewsGrid.innerHTML = reviews.map(review => `
    <div class="card" style="padding:12px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
        <div class="profile-avatar" style="width:32px;height:32px;font-size:14px;">
          ${review.author.charAt(0).toUpperCase()}
        </div>
        <div>
          <strong style="font-size:14px;">${review.author}</strong>
          <div style="display:flex;gap:2px;margin-top:2px;">
            ${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}
          </div>
        </div>
      </div>
      <p style="margin:0;font-size:13px;color:var(--text);">
        ${review.text}
      </p>
      <div style="margin-top:8px;font-size:12px;color:var(--muted);">
        ${review.product}
      </div>
    </div>
  `).join('');
}

// ====================
// МОДАЛЬНЫЕ ОКНА И ФОРМЫ
// ====================

function renderCartModal() {
  const cartItems = document.getElementById('cartItems');
  const cartTotal = document.getElementById('cartTotal');
  
  if (!cartItems || !cartTotal) return;
  
  const items = Object.values(AppState.cart);
  
  if (items.length === 0) {
    cartItems.innerHTML = '<div style="color:var(--muted);text-align:center;padding:20px;">Корзина пуста</div>';
    cartTotal.textContent = '0 ₽';
    return;
  }
  
  cartItems.innerHTML = items.map(item => `
    <div class="cart-item">
      <div class="thumb">
        <img src="${item.thumb}" alt="${item.title}" style="width:100%;height:100%;object-fit:cover;">
      </div>
      <div class="item-info">
        <strong>${item.title}</strong>
        <div style="color:var(--muted);font-size:13px;">${formatPrice(item.price)} × ${item.qty}</div>
        <div class="qty">
          <button data-action="decrease-qty" data-id="${item.id}">−</button>
          <span>${item.qty} шт.</span>
          <button data-action="increase-qty" data-id="${item.id}">+</button>
          <button data-action="remove-from-cart" data-id="${item.id}" style="margin-left:auto;font-size:12px;color:var(--muted);">
            Удалить
          </button>
        </div>
      </div>
    </div>
  `).join('');
  
  cartTotal.textContent = formatPrice(getCartTotal());
}

function setupModalListeners() {
  // Корзина
  const cartBtn = document.getElementById('cartBtn');
  const cartModal = document.getElementById('cartModal');
  const closeCart = document.getElementById('closeCart');
  const clearCartBtn = document.getElementById('clearCart');
  const checkoutBtn = document.getElementById('checkoutBtn');
  
  if (cartBtn && cartModal) {
    cartBtn.addEventListener('click', (e) => {
      e.preventDefault();
      renderCartModal();
      cartModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    });
  }
  
  if (closeCart) {
    closeCart.addEventListener('click', () => {
      cartModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    });
  }
  
  if (clearCartBtn) {
    clearCartBtn.addEventListener('click', () => {
      if (confirm('Очистить корзину?')) {
        clearCart();
        renderCartModal();
      }
    });
  }
  
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', () => {
      const checkoutForm = document.getElementById('checkoutForm');
      if (checkoutForm) {
        checkoutForm.style.display = 'block';
        checkoutBtn.style.display = 'none';
        document.getElementById('clearCart').style.display = 'none';
      }
    });
  }
  
  // Закрытие модальных окон по клику вне
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
      e.target.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
  });
}

function setupListingForms() {
  // Публикации на маркете
  const openListForm = document.getElementById('openListForm');
  const listingForm = document.getElementById('listingForm');
  const cancelListing = document.getElementById('cancelListing');
  const createListing = document.getElementById('createListing');
  
  if (openListForm && listingForm) {
    openListForm.addEventListener('click', () => {
      if (!AppState.user) {
        showToast('Для публикации нужно войти в аккаунт', 'error');
        return;
      }
      listingForm.style.display = 'block';
      openListForm.style.display = 'none';
    });
  }
  
  if (cancelListing && listingForm) {
    cancelListing.addEventListener('click', () => {
      listingForm.style.display = 'none';
      openListForm.style.display = 'block';
    });
  }
  
  if (createListing) {
    createListing.addEventListener('click', async () => {
      const title = document.getElementById('listTitle').value.trim();
      const price = parseFloat(document.getElementById('listPrice').value) || 0;
      const game = document.getElementById('listGame').value.trim();
      const thumb = document.getElementById('listThumb').value.trim();
      
      if (!title || !game) {
        showToast('Заполните название и тему игры', 'error');
        return;
      }
      
      const listingData = {
        title,
        price,
        game_topic: game,
        thumb: thumb || 'https://via.placeholder.com/400x200?text=Публикация',
        description: `Гайд по игре ${game}`
      };
      
      const newListing = await createMarketListing(listingData);
      if (newListing) {
        AppState.marketListings.unshift(newListing);
        renderMarketListings();
        listingForm.style.display = 'none';
        openListForm.style.display = 'block';
        
        // Очищаем форму
        document.getElementById('listTitle').value = '';
        document.getElementById('listPrice').value = '';
        document.getElementById('listGame').value = '';
        document.getElementById('listThumb').value = '';
      }
    });
  }
  
  // Авторские издания
  const openAccListForm = document.getElementById('openAccListForm');
  const accListingForm = document.getElementById('accListingForm');
  const cancelAccListing = document.getElementById('cancelAccListing');
  const createAccListing = document.getElementById('createAccListing');
  
  if (openAccListForm && accListingForm) {
    openAccListForm.addEventListener('click', () => {
      if (!AppState.user) {
        showToast('Для публикации нужно войти в аккаунт', 'error');
        return;
      }
      accListingForm.style.display = 'block';
      openAccListForm.style.display = 'none';
    });
  }
  
  if (cancelAccListing && accListingForm) {
    cancelAccListing.addEventListener('click', () => {
      accListingForm.style.display = 'none';
      openAccListForm.style.display = 'block';
    });
  }
  
  if (createAccListing) {
    createAccListing.addEventListener('click', async () => {
      const title = document.getElementById('accListTitle').value.trim();
      const price = parseFloat(document.getElementById('accListPrice').value) || 0;
      const games = document.getElementById('accListGames').value.trim();
      const thumb = document.getElementById('accListThumb').value.trim();
      
      if (!title || !games) {
        showToast('Заполните название и темы', 'error');
        return;
      }
      
      const listingData = {
        title,
        price,
        topic: games,
        thumb: thumb || 'https://via.placeholder.com/400x200?text=Издание',
        description: `Авторское издание: ${games}`
      };
      
      const newListing = await createAccountListing(listingData);
      if (newListing) {
        AppState.accountListings.unshift(newListing);
        renderAccountListings();
        accListingForm.style.display = 'none';
        openAccListForm.style.display = 'block';
        
        // Очищаем форму
        document.getElementById('accListTitle').value = '';
        document.getElementById('accListPrice').value = '';
        document.getElementById('accListGames').value = '';
        document.getElementById('accListThumb').value = '';
      }
    });
  }
}

// ====================
// ОБРАБОТЧИКИ СОБЫТИЙ
// ====================

function setupEventListeners() {
  // Поиск
  const searchInput = document.getElementById('search');
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        AppState.searchQuery = e.target.value;
        renderProducts();
      }, 300);
    });
  }
  
  // Фильтры категорий
  document.querySelectorAll('[data-cat]').forEach(button => {
    button.addEventListener('click', async (e) => {
      const category = e.target.dataset.cat;
      AppState.currentCategory = category;
      
      document.querySelectorAll('[data-cat]').forEach(btn => {
        btn.setAttribute('aria-pressed', btn === e.target ? 'true' : 'false');
        btn.classList.toggle('active-chip', btn === e.target);
      });
      
      if (category !== 'all') {
        showToast(`Загрузка товаров категории "${category}"...`, 'info');
      }
      
      await loadProducts();
      renderProducts();
    });
  });
  
  // Сортировка
  document.querySelectorAll('[data-sort]').forEach(button => {
    button.addEventListener('click', (e) => {
      const sortType = e.target.dataset.sort;
      AppState.currentSort = sortType;
      
      document.querySelectorAll('[data-sort]').forEach(btn => {
        btn.setAttribute('aria-pressed', btn === e.target ? 'true' : 'false');
        btn.classList.toggle('active-chip', btn === e.target);
      });
      
      renderProducts();
    });
  });
  
  // Глобальные клики
  document.addEventListener('click', handleGlobalClick);
  
  // Модальные окна
  setupModalListeners();
  
  // Формы публикаций
  setupListingForms();
  
  // Чат (упрощенно)
  const chatBtn = document.getElementById('chatBtn');
  const chatModal = document.getElementById('chatModal');
  
  if (chatBtn && chatModal) {
    chatBtn.addEventListener('click', (e) => {
      e.preventDefault();
      chatModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    });
  }
  
  const closeChat = document.getElementById('closeChat');
  if (closeChat) {
    closeChat.addEventListener('click', () => {
      chatModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    });
  }
  
  // Оплата (упрощенно)
  setupPaymentListeners();
}

function handleGlobalClick(e) {
  const button = e.target.closest('[data-action]');
  if (!button) return;
  
  const action = button.dataset.action;
  const itemId = button.dataset.id;
  const itemType = button.dataset.type || 'product';
  
  switch (action) {
    case 'add-to-cart':
      const item = getItemById(itemId, itemType);
      if (item) {
        addToCart(item);
      }
      break;
      
    case 'toggle-favorite':
      const favoriteId = itemType === 'product' ? itemId : `${itemType}-${itemId}`;
      toggleFavorite(favoriteId);
      
      button.setAttribute('aria-pressed', isItemFavorited(favoriteId));
      button.classList.toggle('active-chip', isItemFavorited(favoriteId));
      button.textContent = isItemFavorited(favoriteId) ? 'В избранном' : 'В избранное';
      break;
      
    case 'remove-from-cart':
      removeFromCart(itemId);
      if (document.getElementById('cartModal').getAttribute('aria-hidden') === 'false') {
        renderCartModal();
      }
      break;
      
    case 'increase-qty':
      updateCartQuantity(itemId, (AppState.cart[itemId]?.qty || 0) + 1);
      renderCartModal();
      break;
      
    case 'decrease-qty':
      updateCartQuantity(itemId, (AppState.cart[itemId]?.qty || 0) - 1);
      renderCartModal();
      break;
  }
}

function getItemById(id, type) {
  switch (type) {
    case 'product':
      return AppState.products.find(p => p.id === id);
    case 'market':
      return AppState.marketListings.find(l => l.id === id);
    case 'account':
      return AppState.accountListings.find(l => l.id === id);
    default:
      return null;
  }
}

function setupPaymentListeners() {
  // Выбор способа оплаты
  let currentPaymentMethod = 'card-visa';
  
  document.addEventListener('click', (e) => {
    const chip = e.target.closest('.payment-chip');
    if (!chip) return;
    
    const method = chip.dataset.method;
    currentPaymentMethod = method;
    const paymentMethodHidden = document.getElementById('paymentMethodHidden');
    if (paymentMethodHidden) {
      paymentMethodHidden.value = method;
    }
    
    // Обновляем визуальное состояние
    document.querySelectorAll('.payment-chip').forEach(c => {
      c.classList.toggle('selected', c === chip);
    });
  });
  
  // Подтверждение оплаты
  const confirmPayment = document.getElementById('confirmPayment');
  const cancelCheckout = document.getElementById('cancelCheckout');
  
  if (confirmPayment) {
    confirmPayment.addEventListener('click', () => {
      const name = document.getElementById('checkoutName')?.value.trim() || '';
      const email = document.getElementById('checkoutEmail')?.value.trim() || '';
      const paymentData = document.getElementById('paymentData')?.value.trim() || '';
      
      if (!name || !email) {
        showToast('Введите имя и email', 'error');
        return;
      }
      
      // Симуляция оплаты
      confirmPayment.disabled = true;
      confirmPayment.textContent = 'Обработка...';
      
      setTimeout(() => {
        // Сохраняем заказ
        const order = {
          id: 'ord-' + Date.now(),
          user: AppState.user ? AppState.user.name : name,
          name,
          email,
          method: currentPaymentMethod,
          items: Object.values(AppState.cart),
          total: getCartTotal(),
          created_at: new Date().toISOString()
        };
        
        const orders = JSON.parse(localStorage.getItem('kv_orders') || '[]');
        orders.unshift(order);
        localStorage.setItem('kv_orders', JSON.stringify(orders));
        
        // Очищаем корзину
        clearCart();
        
        // Закрываем модальное окно
        const cartModal = document.getElementById('cartModal');
        if (cartModal) {
          cartModal.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        }
        
        showToast(`Заказ оформлен! Ссылки отправлены на ${email}`, 'success');
        
        // Сбрасываем кнопку
        confirmPayment.disabled = false;
        confirmPayment.textContent = 'Оплатить';
      }, 1500);
    });
  }
  
  if (cancelCheckout) {
    cancelCheckout.addEventListener('click', () => {
      const checkoutForm = document.getElementById('checkoutForm');
      if (checkoutForm) {
        checkoutForm.style.display = 'none';
        const checkoutBtn = document.getElementById('checkoutBtn');
        const clearCartBtn = document.getElementById('clearCart');
        if (checkoutBtn) checkoutBtn.style.display = 'block';
        if (clearCartBtn) clearCartBtn.style.display = 'block';
      }
    });
  }
}

// ====================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ====================

function resetFilters() {
  AppState.currentCategory = 'all';
  AppState.searchQuery = '';
  AppState.currentSort = 'popular';
  
  const searchInput = document.getElementById('search');
  if (searchInput) {
    searchInput.value = '';
  }
  
  document.querySelectorAll('[data-cat]').forEach(btn => {
    const isActive = btn.dataset.cat === 'all';
    btn.setAttribute('aria-pressed', isActive);
    btn.classList.toggle('active-chip', isActive);
  });
  
  document.querySelectorAll('[data-sort]').forEach(btn => {
    const isActive = btn.dataset.sort === 'popular';
    btn.setAttribute('aria-pressed', isActive);
    btn.classList.toggle('active-chip', isActive);
  });
  
  loadProducts().then(() => {
    renderProducts();
    showToast('Фильтры сброшены', 'info');
  });
}

// ====================
// ДЕМО-ДАННЫЕ
// ====================

function getDemoProducts() {
  return [
    {
      id: '1',
      title: 'Гайд по Dota 2: Все герои и стратегии',
      price: 899,
      category: 'Dota 2',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg',
      description: 'Полное руководство по игре Dota 2. Подробные гайды на всех героев, тактики и стратегии командной игры.',
      popularity: 95,
      is_active: true
    },
    {
      id: '2',
      title: 'ФНАФ: Полная история и теория',
      price: 599,
      category: 'FNAF',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/319510/header.jpg',
      description: 'Вся история Five Nights at Freddy\'s от первой до последней части. Анализ лора и теории.',
      popularity: 78,
      is_active: true
    },
    {
      id: '3',
      title: 'Silent Hill 2: Анализ сюжета',
      price: 799,
      category: 'Классика',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/2124490/header.jpg',
      description: 'Глубокий анализ культовой игры. Символизм, персонажи и психологические аспекты сюжета.',
      popularity: 85,
      is_active: true
    },
    {
      id: '4',
      title: 'Гайд по стратегиям в CS:GO',
      price: 499,
      category: 'Стратегия',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg',
      description: 'Советы и стратегии для победы. Тактики на всех картах, руководство по оружию и экономике.',
      popularity: 92,
      is_active: true
    },
    {
      id: '5',
      title: 'Among Us: Полное руководство',
      price: 299,
      category: 'Инди',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/945360/header.jpg',
      description: 'Как выигрывать как предатель и член экипажа. Тактики, психология и анализ поведения.',
      popularity: 67,
      is_active: true
    },
    {
      id: '6',
      title: 'Control: Все секреты и пасхалки',
      price: 699,
      category: 'Анализ',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/870780/header.jpg',
      description: 'Исследование вселенной Control. Поиск всех секретов, пасхалок и связей с другими играми Remedy.',
      popularity: 73,
      is_active: true
    }
  ];
}

function getDemoMarketListings() {
  return [
    {
      id: 'm1',
      title: 'Мой гайд по Dota 2 для новичков',
      price: 199,
      game_topic: 'Dota 2',
      thumb: 'https://via.placeholder.com/400x200/2b5cff/ffffff?text=Dota+Guide',
      description: 'Простой гайд для начинающих игроков'
    }
  ];
}

function getDemoAccountListings() {
  return [
    {
      id: 'a1',
      title: 'Сборник аналитических статей по играм',
      price: 999,
      topic: 'Анализ, Игры',
      thumb: 'https://via.placeholder.com/400x200/00b4d8/ffffff?text=Аналитика',
      description: 'Коллекция глубоких анализов игровых вселенных'
    }
  ];
}

function getDemoReviews() {
  return [
    {
      author: 'Алексей',
      rating: 5,
      text: 'Отличный гайд! Помог улучшить навыки игры.',
      product: 'Гайд по Dota 2'
    },
    {
      author: 'Мария',
      rating: 4,
      text: 'Интересный анализ, много новых деталей узнала.',
      product: 'Silent Hill 2: Анализ'
    },
    {
      author: 'Дмитрий',
      rating: 5,
      text: 'Купил несколько гайдов, все на высшем уровне!',
      product: 'Разные гайды'
    }
  ];
}

// ====================
// ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
// ====================

async function initApp() {
  try {
    console.log('Инициализация приложения с API...');
    
    // Загружаем состояние из localStorage
    loadStateFromStorage();
    
    // Проверяем авторизацию
    checkAuthStatus();
    
    // Загружаем данные с сервера
    await Promise.allSettled([
      loadProducts(),
      loadMarketListings(),
      loadAccountListings()
    ]);
    
    // Рендерим интерфейс
    renderProducts();
    renderMarketListings();
    renderAccountListings();
    renderReviews();
    updateCartCount();
    updateFavCount();
    
    // Настраиваем обработчики событий
    setupEventListeners();
    
    console.log('Приложение успешно инициализировано');
    showToast('Данные успешно загружены', 'success');
    
  } catch (error) {
    console.error('Критическая ошибка инициализации приложения:', error);
    showToast('Ошибка загрузки данных. Используются демо-данные.', 'error');
    
    // Все равно рендерим интерфейс с демо-данными
    renderProducts();
    renderMarketListings();
    renderAccountListings();
    renderReviews();
    updateCartCount();
    updateFavCount();
    setupEventListeners();
  }
}

// ====================
// ЗАПУСК ПРИЛОЖЕНИЯ
// ====================

document.addEventListener('DOMContentLoaded', initApp);

// Экспортируем для глобального использования
window.resetFilters = resetFilters;