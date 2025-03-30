import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/client';

const useAuthStore = create(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      user: null,
      token: null,
      
      // Login and store user data
      login: (userData, token) => {
        localStorage.setItem('token', token);
        set({ 
          isAuthenticated: true, 
          user: userData,
          token: token
        });
      },
      
      // Logout and clear user data
      logout: async () => {
        try {
          // Call the logout endpoint
          await api.post('/auth/jwt/logout');
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear token and state regardless of API success
          localStorage.removeItem('token');
          set({ 
            isAuthenticated: false, 
            user: null,
            token: null
          });
        }
      },
      
      // Fetch current user data
      fetchUserData: async () => {
        try {
          const userData = await api.get('/users/me');
          set({ 
            isAuthenticated: true, 
            user: userData
          });
          return userData;
        } catch (error) {
          console.error('Error fetching user data:', error);
          // If there's an error (like expired token), logout
          get().logout();
          return null;
        }
      }
    }),
    {
      name: 'auth-storage', // name of the item in localStorage
      partialize: (state) => ({ 
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token
      })
    }
  )
);

export default useAuthStore;
