// Local Authentication Service for Docker deployment
const API_URL = import.meta.env.VITE_API_URL || '';

export interface User {
  id: number;
  email: string;
  name: string | null;
  avatar_url: string | null;
  is_verified: boolean;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
  token?: string;
}

const TOKEN_KEY = 'ecolearn_token';
const USER_KEY = 'ecolearn_user';

export const authService = {
  // Get stored token
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  // Get stored user
  getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },

  // Store auth data
  setAuth(token: string, user: User): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Clear auth data
  clearAuth(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  // Register with email/password
  async register(email: string, password: string, name?: string): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Erreur lors de l\'inscription');
    }

    if (data.success && data.token && data.user) {
      this.setAuth(data.token, data.user);
    }

    return data;
  },

  // Login with email/password
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Erreur lors de la connexion');
    }

    if (data.success && data.token && data.user) {
      this.setAuth(data.token, data.user);
    }

    return data;
  },

  // Verify token
  async verifyToken(): Promise<AuthResponse | null> {
    const token = this.getToken();
    if (!token) return null;

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/verify-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        this.clearAuth();
        return null;
      }

      if (data.user) {
        this.setAuth(token, data.user);
      }

      return data;
    } catch {
      this.clearAuth();
      return null;
    }
  },

  // Logout
  async logout(): Promise<void> {
    try {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
        },
      });
    } catch {
      // Ignore errors
    }
    this.clearAuth();
  },

  // Get auth headers for API calls
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
      };
    }
    return {};
  },
};