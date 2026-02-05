/**
 * Auth hook for authentication state and actions.
 */
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store';
import { authAPI } from '../services/api';

export function useAuth() {
  const navigate = useNavigate();
  const { user, isAuthenticated, login: storeLogin, logout: storeLogout, updateUser } = useAuthStore();

  const login = useCallback(async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user } = response.data;
      storeLogin(user, access_token);
      navigate('/');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  }, [storeLogin, navigate]);

  const register = useCallback(async (email, username, password) => {
    try {
      const response = await authAPI.register({ email, username, password });
      const { access_token, user } = response.data;
      storeLogin(user, access_token);
      navigate('/');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  }, [storeLogin, navigate]);

  const logout = useCallback(() => {
    storeLogout();
    navigate('/login');
  }, [storeLogout, navigate]);

  const updateProfile = useCallback(async (data) => {
    try {
      const response = await authAPI.updateMe(data);
      updateUser(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Update failed',
      };
    }
  }, [updateUser]);

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
  };
}
