import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { tenantAPI } from '../lib/api';
import { useAuth } from './AuthContext';

const TenantContext = createContext(null);

export const useTenant = () => {
    const context = useContext(TenantContext);
    if (!context) {
        throw new Error('useTenant must be used within a TenantProvider');
    }
    return context;
};

export const TenantProvider = ({ children }) => {
    const { isAuthenticated } = useAuth();
    const [tenants, setTenants] = useState([]);
    const [currentTenant, setCurrentTenant] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadTenants = useCallback(async () => {
        if (!isAuthenticated) {
            setTenants([]);
            setCurrentTenant(null);
            setLoading(false);
            return;
        }

        try {
            const response = await tenantAPI.getAll();
            setTenants(response.data);
            
            // Set first tenant as current if none selected
            const savedTenantId = localStorage.getItem('currentTenantId');
            const savedTenant = response.data.find(t => t.id === savedTenantId);
            
            if (savedTenant) {
                setCurrentTenant(savedTenant);
            } else if (response.data.length > 0) {
                setCurrentTenant(response.data[0]);
                localStorage.setItem('currentTenantId', response.data[0].id);
            }
        } catch (err) {
            console.error('Failed to load tenants:', err);
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated]);

    useEffect(() => {
        loadTenants();
    }, [loadTenants]);

    const selectTenant = (tenant) => {
        setCurrentTenant(tenant);
        localStorage.setItem('currentTenantId', tenant.id);
    };

    const createTenant = async (data) => {
        try {
            const response = await tenantAPI.create(data);
            const newTenant = response.data;
            setTenants(prev => [...prev, newTenant]);
            if (!currentTenant) {
                selectTenant(newTenant);
            }
            return { success: true, tenant: newTenant };
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Failed to create company' };
        }
    };

    const updateTenant = async (id, data) => {
        try {
            const response = await tenantAPI.update(id, data);
            const updatedTenant = response.data;
            setTenants(prev => prev.map(t => t.id === id ? updatedTenant : t));
            if (currentTenant?.id === id) {
                setCurrentTenant(updatedTenant);
            }
            return { success: true, tenant: updatedTenant };
        } catch (err) {
            return { success: false, error: err.response?.data?.detail || 'Failed to update company' };
        }
    };

    const value = {
        tenants,
        currentTenant,
        loading,
        selectTenant,
        createTenant,
        updateTenant,
        refreshTenants: loadTenants,
    };

    return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
};
