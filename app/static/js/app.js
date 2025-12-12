// /app/static/js/app.js

// Базовый URL API
const API_BASE_URL = 'http://localhost:8000';

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
  searchQuery: ''
};

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
  initApp();
});

async function initApp() {
  try {
    // Загружаем состояние из localStorage
    loadStateFromStorage();
    
    // Проверяем авторизацию
    checkAuthStatus();
    
    // Загружаем данные с сервера
    await Promise.all([
      loadProducts(),
      loadMarketListings(),
      loadAccountListings()
    ]);
    
    // Рендерим начальный интерфейс
    renderProducts();
    renderMarketListings();
    renderAccountListings();
    renderReviews();
    updateCartCount();
    updateFavCount();
    
    // Настраиваем обработчики событий
    setupEventListeners();
    
    console.log('Приложение инициализировано');
  } catch (error) {
    console.error('Ошибка инициализации приложения:', error);
    showToast('Ошибка загрузки данных', 'error');
  }
}

// ====================
// ФУНКЦИИ ДЛЯ РАБОТЫ С API
// ====================

async function loadProducts() {
  try {
    const response = await fetch(`${API_BASE_URL}/products/?skip=0&limit=100`);
    if (response.ok) {
      AppState.products = await response.json();
      // Сохраняем снимок для страницы избранного
      localStorage.setItem('kv_products_snapshot', JSON.stringify(AppState.products));
    }
  } catch (error) {
    console.warn('Не удалось загрузить товары с сервера:', error);
    // Используем демо-данные
    AppState.products = getDemoProducts();
  }
}

async function loadMarketListings() {
  try {
    const response = await fetch(`${API_BASE_URL}/listings/?skip=0&limit=100&active_only=true`);
    if (response.ok) {
      AppState.marketListings = await response.json();
      localStorage.setItem('kv_market_listings', JSON.stringify(AppState.marketListings));
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
      AppState.accountListings = await response.json();
      localStorage.setItem('kv_account_listings', JSON.stringify(AppState.accountListings));
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
// ФУНКЦИИ ДЛЯ РАБОТЫ С АВТОРИЗАЦИЕЙ
// ====================

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
// ФУНКЦИИ ДЛЯ РАБОТЫ С КОРЗИНОЙ
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
  } catch (error) {
    console.error('Ошибка загрузки состояния:', error);
  }
}

function saveCart() {
  localStorage.setItem('kv_cart', JSON.stringify(AppState.cart));
  updateCartCount();
}

function saveFavorites() {
  localStorage.setItem('kv_favs', JSON.stringify(AppState.favorites));
  updateFavCount();
}

function updateCartCount() {
  const cartCount = document.getElementById('cartCount');
  if (cartCount) {
    const count = Object.keys(AppState.cart).length;
    cartCount.textContent = count;
  }
}

function updateFavCount() {
  const favCount = document.getElementById('favCount');
  if (favCount) {
    favCount.textContent = AppState.favorites.length;
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

// ====================
// ФУНКЦИИ ДЛЯ РАБОТЫ С ИЗБРАННЫМ
// ====================

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
// ФУНКЦИИ РЕНДЕРИНГА
// ====================

function renderProducts() {
  const productsContainer = document.getElementById('products');
  if (!productsContainer) return;
  
  // Фильтрация по категории
  let filteredProducts = AppState.products;
  if (AppState.currentCategory !== 'all') {
    filteredProducts = AppState.products.filter(product => 
      (product.category || '').toLowerCase().includes(AppState.currentCategory.toLowerCase()) ||
      (product.title || '').toLowerCase().includes(AppState.currentCategory.toLowerCase())
    );
  }
  
  // Фильтрация по поиску
  if (AppState.searchQuery) {
    filteredProducts = filteredProducts.filter(product =>
      product.title.toLowerCase().includes(AppState.searchQuery.toLowerCase()) ||
      (product.description || '').toLowerCase().includes(AppState.searchQuery.toLowerCase())
    );
  }
  
  // Сортировка
  filteredProducts = sortProducts(filteredProducts, AppState.currentSort);
  
  // Рендеринг
  productsContainer.innerHTML = filteredProducts.map(product => `
    <article class="card" data-id="${product.id}">
      <div class="media">
        <img src="${product.thumb || 'https://via.placeholder.com/400x200?text=No+preview'}" 
             alt="${product.title}"
             onerror="this.src='https://via.placeholder.com/400x200?text=No+preview'">
      </div>
      <div>
        <h3>${product.title}</h3>
        <div class="meta">
          <span class="tag-pill">${product.category || 'Игры'}</span>
          <span class="price">${formatPrice(product.price || 0)}</span>
        </div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">
          ${product.description || 'Электронное издание высокого качества'}
        </p>
      </div>
      <div class="actions">
        <button class="btn primary" data-action="add-to-cart" data-id="${product.id}">
          Купить
        </button>
        <button class="btn ghost ${isItemFavorited(product.id) ? 'active-chip' : ''}" 
                data-action="toggle-favorite" 
                data-id="${product.id}"
                aria-pressed="${isItemFavorited(product.id)}">
          ${isItemFavorited(product.id) ? 'В избранном' : 'В избранное'}
        </button>
      </div>
    </article>
  `).join('');
}

function renderMarketListings() {
  const marketGrid = document.getElementById('marketGrid');
  if (!marketGrid) return;
  
  marketGrid.innerHTML = AppState.marketListings.map(listing => `
    <article class="card" data-id="${listing.id}" data-type="market">
      <div class="media">
        <img src="${listing.thumb || 'https://via.placeholder.com/400x200?text=Публикация'}" 
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
        <img src="${listing.thumb || 'https://via.placeholder.com/400x200?text=Издание'}" 
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

// ====================
// УТИЛИТЫ
// ====================

function formatPrice(price) {
  return price === 0 ? 'Бесплатно' : price.toLocaleString('ru-RU') + ' ₽';
}

function sortProducts(products, sortType) {
  const sorted = [...products];
  
  switch (sortType) {
    case 'price-asc':
      return sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
    case 'price-desc':
      return sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
    case 'popular':
    default:
      return sorted; // В реальном приложении здесь была бы логика популярности
  }
}

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  
  toast.textContent = message;
  toast.className = 'toast';
  toast.classList.add(`toast-${type}`);
  toast.style.display = 'block';
  
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

// ====================
// ОБРАБОТЧИКИ СОБЫТИЙ
// ====================

function setupEventListeners() {
  // Поиск
  const searchInput = document.getElementById('search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      AppState.searchQuery = e.target.value;
      renderProducts();
    });
  }
  
  // Фильтры категорий
  document.querySelectorAll('[data-cat]').forEach(button => {
    button.addEventListener('click', (e) => {
      const category = e.target.dataset.cat;
      AppState.currentCategory = category;
      
      // Обновляем активную кнопку
      document.querySelectorAll('[data-cat]').forEach(btn => {
        btn.setAttribute('aria-pressed', btn === e.target ? 'true' : 'false');
        btn.classList.toggle('active-chip', btn === e.target);
      });
      
      renderProducts();
    });
  });
  
  // Сортировка
  document.querySelectorAll('[data-sort]').forEach(button => {
    button.addEventListener('click', (e) => {
      const sortType = e.target.dataset.sort;
      AppState.currentSort = sortType;
      
      // Обновляем активную кнопку
      document.querySelectorAll('[data-sort]').forEach(btn => {
        btn.setAttribute('aria-pressed', btn === e.target ? 'true' : 'false');
        btn.classList.toggle('active-chip', btn === e.target);
      });
      
      renderProducts();
    });
  });
  
  // Добавление в корзину, избранное и т.д.
  document.addEventListener('click', handleGlobalClick);
  
  // Модальные окна
  setupModalListeners();
  
  // Формы публикаций
  setupListingForms();
  
  // Чат
  setupChatListeners();
  
  // Оплата
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
      
      // Обновляем состояние кнопки
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

function setupChatListeners() {
  const chatBtn = document.getElementById('chatBtn');
  const chatModal = document.getElementById('chatModal');
  const closeChat = document.getElementById('closeChat');
  const chatInput = document.getElementById('chatInput');
  const sendChat = document.getElementById('sendChat');
  const chatBody = document.getElementById('chatBody');
  
  if (chatBtn && chatModal) {
    chatBtn.addEventListener('click', (e) => {
      e.preventDefault();
      loadChatMessages();
      chatModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    });
  }
  
  if (closeChat) {
    closeChat.addEventListener('click', () => {
      chatModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    });
  }
  
  if (sendChat && chatInput && chatBody) {
    sendChat.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendChatMessage();
      }
    });
  }
  
  function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Добавляем сообщение пользователя
    const userMessage = document.createElement('div');
    userMessage.style.cssText = `
      max-width: 80%;
      margin-left: auto;
      padding: 8px 10px;
      border-radius: 10px;
      background: linear-gradient(90deg, #2b5cff, #7b61ff);
      color: #fff;
      font-size: 13px;
    `;
    userMessage.textContent = message;
    chatBody.appendChild(userMessage);
    
    // Очищаем поле ввода
    chatInput.value = '';
    
    // Прокручиваем вниз
    chatBody.scrollTop = chatBody.scrollHeight;
    
    // Имитируем ответ бота
    setTimeout(() => {
      const botMessage = document.createElement('div');
      botMessage.style.cssText = `
        max-width: 80%;
        padding: 8px 10px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        color: var(--text);
        font-size: 13px;
      `;
      botMessage.textContent = 'Спасибо за сообщение! Мы ответим вам в ближайшее время.';
      chatBody.appendChild(botMessage);
      
      // Прокручиваем вниз
      chatBody.scrollTop = chatBody.scrollHeight;
    }, 800);
  }
  
  function loadChatMessages() {
    if (!chatBody) return;
    
    // Загружаем историю чата
    const chatHistory = JSON.parse(localStorage.getItem('kv_chat') || '[]');
    chatBody.innerHTML = '';
    
    if (chatHistory.length === 0) {
      // Первое сообщение бота
      const welcomeMessage = document.createElement('div');
      welcomeMessage.style.cssText = `
        max-width: 80%;
        padding: 8px 10px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        color: var(--text);
        font-size: 13px;
      `;
      welcomeMessage.textContent = 'Здравствуйте! Чем можем помочь?';
      chatBody.appendChild(welcomeMessage);
    } else {
      // Восстанавливаем историю
      chatHistory.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = msg.author === 'user' ? `
          max-width: 80%;
          margin-left: auto;
          padding: 8px 10px;
          border-radius: 10px;
          background: linear-gradient(90deg, #2b5cff, #7b61ff);
          color: #fff;
          font-size: 13px;
        ` : `
          max-width: 80%;
          padding: 8px 10px;
          border-radius: 10px;
          background: rgba(255,255,255,0.03);
          color: var(--text);
          font-size: 13px;
        `;
        messageDiv.textContent = msg.text;
        chatBody.appendChild(messageDiv);
      });
    }
    
    // Прокручиваем вниз
    chatBody.scrollTop = chatBody.scrollHeight;
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
    document.getElementById('paymentMethodHidden').value = method;
    
    // Обновляем визуальное состояние
    document.querySelectorAll('.payment-chip').forEach(c => {
      c.classList.toggle('selected', c === chip);
    });
    
    // Обновляем placeholder для поля данных оплаты
    const paymentDataInput = document.getElementById('paymentData');
    if (method === 'cod') {
      paymentDataInput.style.display = 'none';
      paymentDataInput.placeholder = 'Не требуется';
    } else if (method.startsWith('card')) {
      paymentDataInput.style.display = 'block';
      paymentDataInput.placeholder = 'Номер карты';
    } else if (method === 'paypal' || method === 'qiwi') {
      paymentDataInput.style.display = 'block';
      paymentDataInput.placeholder = `Аккаунт ${method.toUpperCase()}`;
    }
  });
  
  // Подтверждение оплаты
  const confirmPayment = document.getElementById('confirmPayment');
  const cancelCheckout = document.getElementById('cancelCheckout');
  
  if (confirmPayment) {
    confirmPayment.addEventListener('click', () => {
      const name = document.getElementById('checkoutName')?.value.trim() || '';
      const email = document.getElementById('checkoutEmail')?.value.trim() || '';
      const method = document.getElementById('paymentMethodHidden')?.value || 'card-visa';
      const paymentData = document.getElementById('paymentData')?.value.trim() || '';
      
      if (!name || !email) {
        showToast('Введите имя и email', 'error');
        return;
      }
      
      if (method !== 'cod' && !paymentData) {
        showToast('Введите данные для оплаты', 'error');
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
          method,
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
        document.getElementById('cartModal').setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        
        // Сбрасываем форму
        const checkoutForm = document.getElementById('checkoutForm');
        if (checkoutForm) {
          checkoutForm.style.display = 'none';
          document.getElementById('checkoutBtn').style.display = 'block';
          document.getElementById('clearCart').style.display = 'block';
        }
        
        // Сбрасываем кнопку
        confirmPayment.disabled = false;
        confirmPayment.textContent = 'Оплатить';
        
        showToast(`Заказ оформлен! Ссылки отправлены на ${email}`, 'success');
      }, 1500);
    });
  }
  
  if (cancelCheckout) {
    cancelCheckout.addEventListener('click', () => {
      const checkoutForm = document.getElementById('checkoutForm');
      if (checkoutForm) {
        checkoutForm.style.display = 'none';
        document.getElementById('checkoutBtn').style.display = 'block';
        document.getElementById('clearCart').style.display = 'block';
      }
    });
  }
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
      description: 'Полное руководство по игре Dota 2'
    },
    {
      id: '2',
      title: 'ФНАФ: Полная история и теория',
      price: 599,
      category: 'FNAF',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/319510/header.jpg',
      description: 'Вся история Five Nights at Freddy\'s'
    },
    {
      id: '3',
      title: 'Silent Hill 2: Анализ сюжета',
      price: 799,
      category: 'Классика',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/2124490/header.jpg',
      description: 'Глубокий анализ культовой игры'
    },
    {
      id: '4',
      title: 'Гайд по стратегиям в CS:GO',
      price: 499,
      category: 'Стратегия',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg',
      description: 'Советы и стратегии для победы'
    },
    {
      id: '5',
      title: 'Among Us: Полное руководство',
      price: 299,
      category: 'Инди',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/945360/header.jpg',
      description: 'Как выигрывать как предатель и член экипажа'
    },
    {
      id: '6',
      title: 'Control: Все секреты и пасхалки',
      price: 699,
      category: 'Анализ',
      thumb: 'https://cdn.cloudflare.steamstatic.com/steam/apps/870780/header.jpg',
      description: 'Исследование вселенной Control'
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
    },
    {
      id: 'm2',
      title: 'Секреты прохождения ФНАФ',
      price: 299,
      game_topic: 'FNAF',
      thumb: 'https://via.placeholder.com/400x200/7b61ff/ffffff?text=FNAF+Secrets',
      description: 'Как выжить все 5 ночей'
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
    },
    {
      id: 'a2',
      title: 'Артбук по игровым персонажам',
      price: 1499,
      topic: 'Арт, Персонажи',
      thumb: 'https://via.placeholder.com/400x200/28a745/ffffff?text=Артбук',
      description: 'Красивые иллюстрации и концепт-арты'
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
    },
    {
      author: 'Ольга',
      rating: 5,
      text: 'Быстрая доставка, качественный материал.',
      product: 'ФНАФ: История'
    }
  ];
}

// Экспортируем для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AppState,
    addToCart,
    removeFromCart,
    toggleFavorite,
    checkAuthStatus
  };
}