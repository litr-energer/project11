// /app/static/js/api.js
const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  static async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/users/authenticate?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка авторизации');
    }
    
    return await response.json();
  }
  
  static async register(userData) {
    // Получаем роль по умолчанию
    let roleId = 2;
    
    try {
      const rolesResponse = await fetch(`${API_BASE_URL}/roles/`);
      if (rolesResponse.ok) {
        const roles = await rolesResponse.json();
        const defaultRole = roles.find(role => 
          role.name.toLowerCase() === 'user' || 
          role.name.toLowerCase() === 'client'
        );
        if (defaultRole) {
          roleId = defaultRole.id;
        }
      }
    } catch (error) {
      console.warn('Не удалось получить список ролей', error);
    }
    
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        ...userData,
        role_id: roleId
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return await response.json();
  }
  
  static async getUserProfile(userId) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`);
    if (!response.ok) {
      throw new Error('Не удалось получить данные пользователя');
    }
    return await response.json();
  }
  
  static async updateUserProfile(userId, userData) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      throw new Error('Не удалось обновить данные пользователя');
    }
    
    return await response.json();
  }
  
  // Методы для работы с товарами, корзиной и т.д.
  static async getProducts(skip = 0, limit = 100, category = null) {
    let url = `${API_BASE_URL}/products/?skip=${skip}&limit=${limit}`;
    if (category) {
      url += `&category=${encodeURIComponent(category)}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Не удалось получить список товаров');
    }
    
    return await response.json();
  }
  
  static async getCartItems(userId) {
    const response = await fetch(`${API_BASE_URL}/carts/user/${userId}`);
    if (!response.ok) {
      throw new Error('Не удалось получить корзину');
    }
    
    return await response.json();
  }
}

// Экспортируем для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ApiService;
} else {
  window.ApiService = ApiService;
}