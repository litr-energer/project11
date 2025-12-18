// /app/static/js/app.js (ПОЛНЫЙ КОД С ИЗБРАННЫМ ПО АККАУНТУ)

// Базовый URL API
const API_BASE_URL = '';

// Состояние приложения
const AppState = {
  user: null,
  cart: {},
  favorites: [],  // Теперь содержит объекты избранного с сервера
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
// API ФУНКЦИИ ДЛЯ ИЗБРАННОГО
// ====================
function updateFavoriteButtons() {
  document.querySelectorAll('[data-action="toggle-favorite"]').forEach(button => {
    const itemId = button.dataset.id;
    const itemType = button.dataset.type;
    
    if (itemId && itemType) {
      const isFavorited = AppState.user ? isItemFavorited(itemId, itemType) : false;
      
      button.setAttribute('aria-pressed', isFavorited);
      button.classList.toggle('active-chip', isFavorited);
      button.textContent = AppState.user ? (isFavorited ? 'В избранном' : 'В избранное') : 'В избранное';
    }
  });
}

async function loadUserFavorites() {
  try {
    const user = AppState.user;
    if (!user) {
      AppState.favorites = [];
      updateFavCount();
      updateFavoriteButtons(); // Обновляем кнопки
      return [];
    }
    
    console.log('Загрузка избранного для пользователя:', user.id);
    
    const response = await fetch(`${API_BASE_URL}/favorites/user/${user.id}?skip=0&limit=100`);
    
    if (response.ok) {
      const favoritesData = await response.json();
      console.log('Загружены избранные с сервера:', favoritesData);
      
      // Сохраняем полные объекты избранного
      AppState.favorites = favoritesData;
      
      updateFavCount();
      updateFavoriteButtons(); // ОБНОВЛЯЕМ КНОПКИ ПОСЛЕ ЗАГРУЗКИ
      console.log('Избранное загружено:', AppState.favorites.length, 'шт.');
      return AppState.favorites;
    } else {
      console.warn('Ошибка загрузки избранного:', response.status);
      showToast('Ошибка загрузки избранного', 'error');
      return [];
    }
  } catch (error) {
    console.error('Ошибка загрузки избранного:', error);
    showToast('Ошибка загрузки избранного', 'error');
    return [];
  }
}

async function addToFavorites(itemId, itemType) {
  try {
    const user = AppState.user;
    if (!user) {
      showToast('Для добавления в избранное нужно войти в аккаунт', 'error');
      return { success: false, isFavorited: false };
    }
    
    const favoriteData = {
      user_id: user.id
    };
    
    // Определяем тип товара
    const id = parseInt(itemId);
    if (isNaN(id)) {
      throw new Error('Неверный ID товара');
    }
    
    if (itemType === 'product') {
      favoriteData.products_id = id;
    } else if (itemType === 'market') {
      favoriteData.listing_id = id;
    } else if (itemType === 'account') {
      favoriteData.author_listing_id = id;
    } else {
      throw new Error('Неизвестный тип товара');
    }
    
    console.log('Добавление в избранное:', favoriteData);
    
    const response = await fetch(`${API_BASE_URL}/favorites/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(favoriteData)
    });
    
    if (response.ok) {
      const newFavorite = await response.json();
      
      // Добавляем в локальное состояние
      AppState.favorites.push(newFavorite);
      
      updateFavCount();
      console.log('Добавлено в избранное:', newFavorite);
      showToast('Добавлено в избранное', 'success');
      return { success: true, isFavorited: true, favorite: newFavorite };
      
    } else if (response.status === 409) {
      // Уже в избранном
      console.log('Товар уже в избранном');
      showToast('Уже в избранном', 'info');
      return { success: true, isFavorited: true };
      
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Ошибка: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка добавления в избранное:', error);
    showToast(error.message || 'Ошибка добавления в избранное', 'error');
    return { success: false, isFavorited: false };
  }
}

async function removeFromFavorites(itemId, itemType) {
  try {
    const user = AppState.user;
    if (!user) {
      showToast('Нужно войти в аккаунт', 'error');
      return { success: false, isFavorited: true };
    }
    
    // Находим запись избранного
    const favorite = findFavoriteByItem(itemId, itemType);
    if (!favorite) {
      console.warn('Запись избранного не найдена локально');
      // Все равно удаляем из локального состояния
      removeFavoriteFromLocalState(itemId, itemType);
      return { success: true, isFavorited: false };
    }
    
    const response = await fetch(`${API_BASE_URL}/favorites/${favorite.id}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      // Удаляем из локального состояния
      const index = AppState.favorites.findIndex(f => f.id === favorite.id);
      if (index > -1) {
        AppState.favorites.splice(index, 1);
      }
      
      updateFavCount();
      console.log('Удалено из избранного:', favorite.id);
      showToast('Удалено из избранного', 'info');
      return { success: true, isFavorited: false };
      
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Ошибка: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка удаления из избранного:', error);
    showToast(error.message || 'Ошибка удаления из избранного', 'error');
    return { success: false, isFavorited: true };
  }
}

function findFavoriteByItem(itemId, itemType) {
  const id = parseInt(itemId);
  if (isNaN(id)) return null;
  
  return AppState.favorites.find(fav => {
    if (itemType === 'product') return fav.products_id === id;
    if (itemType === 'market') return fav.listing_id === id;
    if (itemType === 'account') return fav.author_listing_id === id;
    return false;
  });
}


function removeFavoriteFromLocalState(itemId, itemType) {
  const favorite = findFavoriteByItem(itemId, itemType);
  if (favorite) {
    const index = AppState.favorites.findIndex(f => f.id === favorite.id);
    if (index > -1) {
      AppState.favorites.splice(index, 1);
      updateFavCount();
    }
  }
}

function isItemFavorited(itemId, itemType) {
  // Приводим itemId к числу для сравнения
  const id = parseInt(itemId);
  if (isNaN(id)) return false;
  
  return AppState.favorites.some(fav => {
    if (itemType === 'product') return fav.products_id === id;
    if (itemType === 'market') return fav.listing_id === id;
    if (itemType === 'account') return fav.author_listing_id === id;
    return false;
  });
}

function updateFavCount() {
  const favCount = document.getElementById('favCount');
  if (favCount) {
    favCount.textContent = AppState.favorites.length;
  }
}

// ====================
// ФУНКЦИЯ ПЕРЕКЛЮЧЕНИЯ ИЗБРАННОГО
// ====================

async function toggleFavorite(itemId, itemType) {
  // Если пользователь не авторизован, показываем сообщение
  if (!AppState.user) {
    showToast('Для добавления в избранное нужно войти в аккаунт', 'error');
    return false;
  }
  
  const isCurrentlyFavorited = isItemFavorited(itemId, itemType);
  
  if (isCurrentlyFavorited) {
    // Удаляем из избранного
    const result = await removeFromFavorites(itemId, itemType);
    return !result.isFavorited; // Возвращаем новое состояние
  } else {
    // Добавляем в избранное
    const result = await addToFavorites(itemId, itemType);
    return result.isFavorited; // Возвращаем новое состояние
  }
}

// ====================
// API ФУНКЦИИ ДЛЯ КОРЗИНЫ
// ====================

async function loadUserCart() {
  try {
    const user = AppState.user;
    if (!user) {
      console.log('Пользователь не авторизован, используем локальную корзину');
      AppState.cart = AppState.cart || {};
      saveCart();
      updateCartCount();
      return null;
    }
    
    console.log('Загрузка корзины пользователя:', user.id);
    
    // Просто возвращаем существующую корзину без запросов к API
    // (для отладки, потом вернете запросы)
    console.log('Текущая корзина:', AppState.cart);
    updateCartCount();
    return AppState.cart;
    
  } catch (error) {
    console.error('Ошибка загрузки корзины:', error);
    return null;
  }
}

async function fetchItemDetails(itemType, itemId) {
  try {
    let url = '';
    
    if (itemType === 'product') {
      url = `/products/${itemId}`;
    } else if (itemType === 'listing') {
      url = `${API_BASE_URL}/listings/${itemId}`;
    } else if (itemType === 'author_listing') {
      url = `${API_BASE_URL}/author-listings/${itemId}`;
    } else {
      return null;
    }
    
    console.log(`Загружаем детали товара: ${url}`);
    const response = await fetch(url);
    
    if (response.ok) {
      const itemData = await response.json();
      console.log('Загружен товар с сервера:', itemData);
      
      // Преобразуем данные в единый формат
      return {
        id: itemData.id?.toString() || itemId,
        title: itemData.title || 'Без названия',
        description: itemData.description || '',
        price: itemData.price || 0,
        thumb: itemData.image_url || itemData.thumbnail || itemData.thumb || 'https://via.placeholder.com/160x90',
        category: itemData.category || itemData.game_topic || itemData.topic || 'Товар',
        // Сохраняем оригинальные данные
        raw_data: itemData
      };
    }
  } catch (error) {
    console.error(`Ошибка загрузки товара ${itemId}:`, error);
  }
  
  return null;
}

async function addItemToCartAPI(item, itemType) {
  try {
    const user = AppState.user;
    if (!user) {
      // Для неавторизованных пользователей - локальная корзина
      const itemId = `local-${item.id}-${Date.now()}`;
      AppState.cart[itemId] = {
        id: itemId,
        title: item.title,
        price: item.price || 0,
        qty: 1,
        thumb: item.thumb || 'https://via.placeholder.com/160x90',
        category: item.category || item.game_topic || item.topic || 'Товар',
        item_type: itemType,
        item_id: item.id,
        description: item.description || '',
        local: true
      };
      saveCart();
      updateCartCount();
      showToast(`"${item.title}" добавлен в корзину`, 'success');
      return { success: true, cartItem: AppState.cart[itemId] };
    }
    
    console.log('Добавление товара в корзину:', item);
    
    // Подготавливаем данные для API
    const requestData = {
      item_type: itemType,
      quantity: 1,
      price: item.price || 0
    };
    
    // Добавляем правильное поле ID
    const id = parseInt(item.id);
    if (itemType === 'product') {
      requestData.product_id = id;
    } else if (itemType === 'market') {
      requestData.listing_id = id;
    } else if (itemType === 'account') {
      requestData.author_listing_id = id;
    }
    
    console.log('Отправка в API:', requestData);
    
    const response = await fetch(`${API_BASE_URL}/carts/my/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': user.id.toString()
      },
      body: JSON.stringify(requestData)
    });
    
    if (response.ok) {
      const cartItem = await response.json();
      console.log('Ответ от сервера:', cartItem);
      
      // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем ВСЕ данные из карточки товара
      const cartItemId = `cart-${cartItem.id}`;
      AppState.cart[cartItemId] = {
        id: cartItemId,
        title: item.title, // Берем из карточки товара
        price: item.price || 0,
        qty: cartItem.quantity,
        thumb: item.thumb || item.image_url || 'https://via.placeholder.com/160x90',
        category: item.category || item.game_topic || item.topic || 'Товар',
        description: item.description || '',
        api_id: cartItem.id,
        item_type: itemType,
        item_id: item.id,
        // Сохраняем все исходные данные
        source_data: item
      };
      
      saveCart();
      updateCartCount();
      
      showToast(`"${item.title}" добавлен в корзину`, 'success');
      console.log('Товар сохранен в локальной корзине:', AppState.cart[cartItemId]);
      return { success: true, cartItem };
    } else {
      const errorText = await response.text();
      console.error('Ошибка API:', errorText);
      
      // Fallback: добавляем в локальную корзину
      const fallbackId = `fallback-${item.id}-${Date.now()}`;
      AppState.cart[fallbackId] = {
        id: fallbackId,
        title: item.title,
        price: item.price || 0,
        qty: 1,
        thumb: item.thumb || 'https://via.placeholder.com/160x90',
        category: item.category || item.game_topic || item.topic || 'Товар',
        description: item.description || '',
        item_type: itemType,
        item_id: item.id,
        local: true,
        source_data: item
      };
      
      saveCart();
      updateCartCount();
      showToast(`"${item.title}" добавлен в локальную корзину`, 'success');
      
      return { success: false, error: errorText };
    }
  } catch (error) {
    console.error('Ошибка добавления в корзину:', error);
    
    // Добавляем в локальную корзину при любой ошибке
    const errorId = `error-${item.id}-${Date.now()}`;
    AppState.cart[errorId] = {
      id: errorId,
      title: item.title,
      price: item.price || 0,
      qty: 1,
      thumb: item.thumb || 'https://via.placeholder.com/160x90',
      category: item.category || item.game_topic || item.topic || 'Товар',
      description: item.description || '',
      item_type: itemType,
      item_id: item.id,
      local: true,
      source_data: item
    };
    
    saveCart();
    updateCartCount();
    showToast(`"${item.title}" добавлен в корзину (оффлайн)`, 'warning');
    
    return { success: false, error: error.message };
  }
}

async function updateCartItemQuantityAPI(cartItemId, newQty) {
  try {
    const user = AppState.user;
    if (!user) {
      // Для неавторизованных пользователей обновляем локально
      updateCartQuantity(cartItemId, newQty);
      return { success: true };
    }
    
    const cartItem = AppState.cart[cartItemId];
    if (!cartItem || !cartItem.api_id) {
      console.warn('API ID не найден для:', cartItemId);
      return { success: false, error: 'Cart item not found' };
    }
    
    const response = await fetch(`${API_BASE_URL}/carts/my/items/${cartItem.api_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': user.id.toString()
      },
      body: JSON.stringify({ quantity: newQty })
    });
    
    if (response.ok) {
      const updatedItem = await response.json();
      
      // Обновляем локальное состояние
      if (newQty <= 0) {
        delete AppState.cart[cartItemId];
      } else {
        cartItem.qty = newQty;
      }
      
      saveCart();
      updateCartCount();
      
      return { success: true, updatedItem };
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Ошибка: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка обновления количества:', error);
    return { success: false, error: error.message };
  }
}

async function removeItemFromCartAPI(cartItemId) {
  try {
    const user = AppState.user;
    if (!user) {
      // Для неавторизованных пользователей удаляем локально
      removeFromCart(cartItemId);
      return { success: true };
    }
    
    const cartItem = AppState.cart[cartItemId];
    if (!cartItem || !cartItem.api_id) {
      console.warn('API ID не найден для:', cartItemId);
      return { success: false, error: 'Cart item not found' };
    }
    
    const response = await fetch(`${API_BASE_URL}/carts/my/items/${cartItem.api_id}`, {
      method: 'DELETE',
      headers: {
        'X-User-Id': user.id.toString()
      }
    });
    
    if (response.ok) {
      // Удаляем из локального состояния
      delete AppState.cart[cartItemId];
      saveCart();
      updateCartCount();
      
      return { success: true };
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Ошибка: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка удаления из корзины:', error);
    return { success: false, error: error.message };
  }
}

async function clearCartAPI() {
  try {
    const user = AppState.user;
    if (!user) {
      // Для неавторизованных пользователей очищаем локально
      clearCart();
      return { success: true };
    }
    
    const response = await fetch(`${API_BASE_URL}/carts/my/clear`, {
      method: 'DELETE',
      headers: {
        'X-User-Id': user.id.toString()
      }
    });
    
    if (response.ok) {
      // Очищаем локальное состояние
      AppState.cart = {};
      saveCart();
      updateCartCount();
      
      return { success: true };
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Ошибка: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка очистки корзины:', error);
    return { success: false, error: error.message };
  }
}

// ====================
// ЗАГРУЗКА СОСТОЯНИЯ И АВТОРИЗАЦИЯ
// ====================

function loadStateFromStorage() {
  try {
    // Корзина
    const cart = JSON.parse(localStorage.getItem('kv_cart') || '{}');
    AppState.cart = cart;
    
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

async function checkAuthStatus() {
  const user = JSON.parse(localStorage.getItem('kv_user') || 'null');
  const authArea = document.getElementById('authArea');
  const userProfile = document.getElementById('userProfile');
  const authButtons = document.getElementById('authButtons');
  const cartBtn = document.getElementById('cartBtn');
  
  if (user && user.name && user.id) {
    AppState.user = user;
    
    // Пользователь авторизован
    if (userProfile) userProfile.style.display = 'flex';
    if (authButtons) authButtons.style.display = 'none';
    if (cartBtn) cartBtn.style.display = 'block'; // Показываем корзину
    
    // Обновляем аватар и имя
    updateUserProfileUI(user);
    
    // Загружаем избранное пользователя
    await loadUserFavorites();
    
    // Загружаем корзину пользователя
    await loadUserCart();
    
    // Обновляем кнопки избранного на странице
    updateFavoriteButtons();
    
    // Добавляем обработчик выхода
    setupLogoutHandler();
  } else {
    // Пользователь не авторизован
    AppState.user = null;
    AppState.favorites = []; // Очищаем избранное при выходе
    if (userProfile) userProfile.style.display = 'none';
    if (authButtons) authButtons.style.display = 'flex';
    if (cartBtn) cartBtn.style.display = 'none'; // СКРЫВАЕМ КОРЗИНУ
    
    // Обновляем кнопки избранного на странице
    updateFavoriteButtons();
  }
  
  updateFavCount();
  updateCartCount();
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
  AppState.favorites = []; // Очищаем избранное
  checkAuthStatus();
  showToast('Вы вышли из аккаунта', 'info');
}

// ====================
// КОРЗИНА (ЛОКАЛЬНЫЕ ФУНКЦИИ)
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
  
  // Если пользователь авторизован, сохраняем в API
  if (AppState.user) {
    const itemType = item.item_type || 'product'; // Определяем тип
    addItemToCartAPI(item, itemType);
  } else {
    saveCart();
  }
  
  showToast(`"${item.title}" добавлен в корзину`, 'success');
}

function removeFromCart(itemId) {
  if (AppState.cart[itemId]) {
    // Если пользователь авторизован, удаляем из API
    if (AppState.user && AppState.cart[itemId].api_id) {
      removeItemFromCartAPI(itemId);
    } else {
      delete AppState.cart[itemId];
      saveCart();
    }
    showToast('Товар удален из корзины', 'info');
  }
}

function updateCartQuantity(itemId, newQty) {
  if (AppState.cart[itemId]) {
    if (newQty <= 0) {
      removeFromCart(itemId);
    } else {
      // Если пользователь авторизован, обновляем в API
      if (AppState.user && AppState.cart[itemId].api_id) {
        updateCartItemQuantityAPI(itemId, newQty);
      } else {
        AppState.cart[itemId].qty = newQty;
        saveCart();
      }
    }
  }
}

function clearCart() {
  // Если пользователь авторизован, очищаем в API
  if (AppState.user) {
    clearCartAPI();
  } else {
    AppState.cart = {};
    saveCart();
  }
  showToast('Корзина очищена', 'info');
}

function getCartTotal() {
  return Object.values(AppState.cart).reduce((total, item) => {
    return total + (item.price * item.qty);
  }, 0);
}

// ====================
// API ФУНКЦИИ ДЛЯ ТОВАРОВ
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
      const isActive = product.is_active !== false;
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
        is_active: isActive,
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
      const errorText = await response.text();
      console.error('Ошибка API маркетплейса:', errorText);
      throw new Error('Ошибка создания публикации на маркетплейсе');
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
    
    console.log('Отправка авторского издания на сервер:', listingData);
    
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
    
    console.log('Ответ сервера:', response.status, response.statusText);
    
    if (response.ok) {
      const newListing = await response.json();
      console.log('Авторское издание успешно создано:', newListing);
      showToast('Авторское издание успешно создано!', 'success');
      return newListing;
    } else {
      // Пытаемся распарсить ошибку
      let errorMessage = 'Ошибка создания издания';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (parseError) {
        // Если не можем распарсить JSON, используем текст ошибки
        const errorText = await response.text();
        console.error('Текст ошибки:', errorText);
        errorMessage = `Ошибка сервера (${response.status}): ${errorText || response.statusText}`;
      }
      throw new Error(errorMessage);
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
          ${('★').repeat(Math.min(Math.floor(product.popularity / 20), 5))}
          ${('☆').repeat(5 - Math.min(Math.floor(product.popularity / 20), 5))}
         </div>`
      : '';
    
    // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Правильно проверяем избранное
    const isFavorited = AppState.user ? isItemFavorited(product.id, 'product') : false;
    
    return `
      <article class="card" data-id="${product.id}" data-type="product" data-category="${product.category}">
        <div class="media" style="position: relative;">
          <img src="${product.thumb}" 
               alt="${product.title}"
               loading="lazy"
               style="width: 100%; height: 100%; object-fit: cover;" 
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
          <button class="btn ghost ${isFavorited ? 'active-chip' : ''}" 
                  data-action="toggle-favorite" 
                  data-id="${product.id}"
                  data-type="product"
                  aria-pressed="${isFavorited}"
                  ${!product.is_active ? 'disabled style="opacity: 0.5;"' : ''}
                  ${!AppState.user ? 'title="Войдите чтобы добавить в избранное"' : ''}>
            ${AppState.user ? (isFavorited ? 'В избранном' : 'В избранное') : 'В избранное'}
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
  
  marketGrid.innerHTML = AppState.marketListings.map(listing => {
    // Правильно проверяем избранное для публикаций
    const isFavorited = AppState.user ? isItemFavorited(listing.id, 'market') : false;
    
    return `
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
        <button class="btn ghost ${isFavorited ? 'active-chip' : ''}" 
                data-action="toggle-favorite" 
                data-id="${listing.id}"
                data-type="market"
                aria-pressed="${isFavorited}"
                ${!AppState.user ? 'title="Войдите чтобы добавить в избранное"' : ''}>
          ${AppState.user ? (isFavorited ? 'В избранном' : 'В избранное') : 'В избранное'}
        </button>
      </div>
    </article>
  `}).join('');
}

function renderAccountListings() {
  const accMarketGrid = document.getElementById('accMarketGrid');
  if (!accMarketGrid) return;
  
  accMarketGrid.innerHTML = AppState.accountListings.map(listing => {
    // Правильно проверяем избранное для авторских изданий
    const isFavorited = AppState.user ? isItemFavorited(listing.id, 'account') : false;
    
    return `
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
        <button class="btn ghost ${isFavorited ? 'active-chip' : ''}" 
                data-action="toggle-favorite" 
                data-id="${listing.id}"
                data-type="account"
                aria-pressed="${isFavorited}"
                ${!AppState.user ? 'title="Войдите чтобы добавить в избранное"' : ''}>
          ${AppState.user ? (isFavorited ? 'В избранном' : 'В избранное') : 'В избранное'}
        </button>
      </div>
    </article>
  `}).join('');
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
            ${('★').repeat(review.rating)}${('☆').repeat(5-review.rating)}
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
  
  cartItems.innerHTML = items.map(item => {
    // Используем полные данные, если есть
    const title = item.title || `Товар #${item.item_id || item.id}`;
    const thumb = item.thumb || 'https://via.placeholder.com/60x60?text=Товар';
    const category = item.category || 'Товар';
    
    // Цвет категории
    const categoryColor = getCategoryColor(category);
    
    // Форматируем цены
    const itemPrice = formatPrice(item.price);
    const itemTotal = formatPrice(item.price * item.qty);
    
    return `
    <div class="cart-item" style="
      display: flex; gap: 12px; padding: 12px; 
      border-bottom: 1px solid rgba(255,255,255,0.05);
      align-items: center;
    ">
      <!-- Изображение -->
      <div style="width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0;">
        <img src="${thumb}" alt="${title}" 
             style="width: 100%; height: 100%; object-fit: cover;"
             onerror="this.src='https://via.placeholder.com/60x60?text=Товар'">
      </div>
      
      <!-- Информация -->
      <div style="flex: 1; min-width: 0;">
        <!-- Заголовок и цена -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
          <div>
            <strong style="display: block; font-size: 14px; margin-bottom: 4px;">${title}</strong>
            <div style="display: flex; gap: 6px; align-items: center;">
              <span style="
                background: ${categoryColor}; 
                color: white; padding: 2px 8px; 
                border-radius: 12px; font-size: 11px;
              ">${category}</span>
              ${item.item_type !== 'product' ? 
                `<span style="font-size:11px;color:#aaa;">
                  ${item.item_type === 'market' ? '👤 Публикация' : '✍️ Авторское'}
                </span>` : ''
              }
            </div>
          </div>
          <div style="font-weight: bold; color: var(--accent-1); font-size: 16px;">
            ${itemTotal}
          </div>
        </div>
        
        <!-- Описание (если есть) -->
        ${item.description ? `
          <div style="font-size: 12px; color: var(--muted); margin-bottom: 8px; line-height: 1.3;">
            ${item.description.length > 60 ? item.description.substring(0, 60) + '...' : item.description}
          </div>
        ` : ''}
        
        <!-- Управление количеством -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <button data-action="decrease-qty" data-id="${item.id}" 
                    style="width: 24px; height: 24px; border-radius: 50%; border: none;
                           background: rgba(255,255,255,0.1); color: white; cursor: pointer;">
              −
            </button>
            <span style="font-weight: bold; min-width: 30px; text-align: center;">${item.qty} шт.</span>
            <button data-action="increase-qty" data-id="${item.id}"
                    style="width: 24px; height: 24px; border-radius: 50%; border: none;
                           background: rgba(255,255,255,0.1); color: white; cursor: pointer;">
              +
            </button>
            <span style="font-size: 13px; color: var(--muted);">
              ${itemPrice} × ${item.qty}
            </span>
          </div>
          
          <button data-action="remove-from-cart" data-id="${item.id}" 
                  style="background: none; border: none; color: #ff6b6b; 
                         cursor: pointer; font-size: 13px; padding: 4px 8px;">
            Удалить
          </button>
        </div>
      </div>
    </div>
    `;
  }).join('');
  
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

async function handleGlobalClick(e) {
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
      const isNowFavorited = await toggleFavorite(itemId, itemType);
      
      // Обновляем конкретную кнопку
      button.setAttribute('aria-pressed', isNowFavorited);
      button.classList.toggle('active-chip', isNowFavorited);
      button.textContent = AppState.user ? (isNowFavorited ? 'В избранном' : 'В избранное') : 'В избранное';
      
      // Также обновляем все кнопки на случай, если есть дубли
      updateFavoriteButtons();
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
  console.log(`Поиск товара: id=${id}, type=${type}`);
  
  let item = null;
  
  if (type === 'product') {
    item = AppState.products.find(p => {
      console.log(`Сравниваем: p.id=${p.id} (${typeof p.id}) с ${id} (${typeof id})`);
      return p.id == id || p.id.toString() === id.toString();
    });
  } else if (type === 'market') {
    item = AppState.marketListings.find(l => l.id == id || l.id.toString() === id.toString());
  } else if (type === 'account') {
    item = AppState.accountListings.find(a => a.id == id || a.id.toString() === id.toString());
  }
  
  console.log('Найден товар:', item);
  return item;
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
    
    // Проверяем авторизацию и загружаем избранное
    await checkAuthStatus();
    
    // Загружаем остальные данные с сервера
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
    
    // Настраиваем обработчики событий
    setupEventListeners();
    
    // Обновляем кнопку чата
    updateChatButton();
    
    console.log('Приложение успешно инициализировано');
    console.log('Пользователь:', AppState.user ? 'авторизован' : 'не авторизован');
    console.log('Избранных товаров:', AppState.favorites.length);
    console.log('Товаров в корзине:', Object.keys(AppState.cart).length);
    
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
    setupEventListeners();
    updateChatButton();
  }
}

// ====================
// ЗАПУСК ПРИЛОЖЕНИЯ
// ====================

document.addEventListener('DOMContentLoaded', initApp);

// Экспортируем для глобального использования
window.resetFilters = resetFilters;
window.AppState = AppState;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.clearCart = clearCart;
window.toggleFavorite = toggleFavorite;
window.isItemFavorited = isItemFavorited;
window.loadUserFavorites = loadUserFavorites;

// ====================
// ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ЧАТА
// ====================

function updateChatButton() {
  const chatBtn = document.getElementById('chatBtn');
  if (chatBtn) {
    chatBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const user = AppState.user;
      if (!user) {
        showToast('Для доступа к чату необходимо авторизоваться', 'error');
        setTimeout(() => {
          window.location.href = '/auth.html?redirect=/chat.html';
        }, 1500);
        return;
      }
      window.location.href = '/chat.html';
    });
  }
}

function getCategoryColor(category) {
  const categoryLower = (category || '').toLowerCase();
  const colors = {
    'dota 2': '#2b5cff',
    'dota2': '#2b5cff',
    'fnaf': '#7b61ff',
    'классика': '#28a745',
    'стратегия': '#fd7e14',
    'инди': '#e83e8c',
    'анализ': '#17a2b8',
    'гайды': '#6f42c1',
    'лор': '#20c997',
    'маркет': '#00b4d8',
    'авторское': '#e83e8c'
  };
  return colors[categoryLower] || 'rgba(102, 126, 234, 0.8)';
}