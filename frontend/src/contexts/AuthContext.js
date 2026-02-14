import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../lib/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadUser = useCallback(async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await authAPI.getMe();
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
        } catch (err) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadUser();
    }, [loadUser]);

    const login = async (email, password) => {
        try {
            setError(null);
            const response = await authAPI.login({ email, password });
            const { access_token, user: userData } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));
            setUser(userData);
            return { success: true };
        } catch (err) {
            const message = err.response?.data?.detail || 'Login failed';
            setError(message);
            return { success: false, error: message };
        }
    };

    const register = async (email, password, name, role = 'sme_user') => {
        try {
            setError(null);
            const response = await authAPI.register({ email, password, name, role });
            const { access_token, user: userData } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));
            setUser(userData);
            return { success: true };
        } catch (err) {
            const message = err.response?.data?.detail || 'Registration failed';
            setError(message);
            return { success: false, error: message };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    };

    const requestPasswordReset = async (email) => {
        try {
            await authAPI.requestPasswordReset(email);
            return { success: true };
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Request failed' };
        }
    };

    const confirmPasswordReset = async (token, newPassword) => {
        try {
            await authAPI.confirmPasswordReset(token, newPassword);
            return { success: true };
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Reset failed' };
        }
    };

    const isAdmin = user?.role === 'admin';
    const isAccountant = user?.role === 'accountant' || isAdmin;

    const value = {
        user,
        loading,
        error,
        login,
        register,
        logout,
        requestPasswordReset,
        confirmPasswordReset,
        isAdmin,
        isAccountant,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
