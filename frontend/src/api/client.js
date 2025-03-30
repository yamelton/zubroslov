const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default {
  async get(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    return handleResponse(response);
  },

  async post(endpoint, body) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    });
    return handleResponse(response);
  },

  async postForm(endpoint, formData) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });
    return handleResponse(response);
  },

  async put(endpoint, body) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    });
    return handleResponse(response);
  }
};

async function handleResponse(response) {
  if (!response.ok) {
    // Handle different error status codes
    if (response.status === 401) {
      // Unauthorized - could be expired token
      throw new Error('Unauthorized');
    } else if (response.status === 400) {
      // Bad request - likely invalid credentials
      throw new Error('LOGIN_BAD_CREDENTIALS');
    } else if (response.status === 404) {
      // Not found
      throw new Error('Resource not found');
    }
    
    // Try to parse error details from response
    try {
      const error = await response.json();
      throw new Error(error.detail || `Request failed with status ${response.status}`);
    } catch (e) {
      // If parsing fails, throw generic error with status code
      throw new Error(`Request failed with status ${response.status}`);
    }
  }
  
  // For successful responses, parse JSON
  try {
    return await response.json();
  } catch (e) {
    // Handle case where response is not JSON
    return { success: true };
  }
}
