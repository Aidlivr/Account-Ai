import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    getMe: () => api.get('/auth/me'),
    requestPasswordReset: (email) => api.post('/auth/password-reset/request', { email }),
    confirmPasswordReset: (token, newPassword) => api.post('/auth/password-reset/confirm', { token, new_password: newPassword }),
    refreshToken: () => api.post('/auth/refresh'),
};

// Tenant API
export const tenantAPI = {
    create: (data) => api.post('/tenants/', data),
    getAll: () => api.get('/tenants/'),
    getOne: (id) => api.get(`/tenants/${id}`),
    update: (id, data) => api.put(`/tenants/${id}`, data),
    addUser: (tenantId, email) => api.post(`/tenants/${tenantId}/users/${email}`),
};

// Document API
export const documentAPI = {
    upload: (file, tenantId) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('tenant_id', tenantId);
        return api.post('/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    getAll: (tenantId = null, status = null) => {
        const params = new URLSearchParams();
        if (tenantId) params.append('tenant_id', tenantId);
        if (status) params.append('status', status);
        return api.get(`/documents/?${params.toString()}`);
    },
    getOne: (id) => api.get(`/documents/${id}`),
    approve: (id, approved, modifications = null) => 
        api.put(`/documents/${id}/approve`, { approved, modifications }),
};

// Reconciliation API
export const reconciliationAPI = {
    getUnmatched: (tenantId) => api.get(`/reconciliation/${tenantId}/unmatched`),
    match: (tenantId, data) => api.post(`/reconciliation/${tenantId}/match`, data),
    bulkApprove: (tenantId, matches) => api.post(`/reconciliation/${tenantId}/bulk-approve`, matches),
};

// VAT API
export const vatAPI = {
    getAnalysis: (tenantId, periodStart = null, periodEnd = null) => {
        const params = new URLSearchParams();
        if (periodStart) params.append('period_start', periodStart);
        if (periodEnd) params.append('period_end', periodEnd);
        return api.get(`/vat/${tenantId}/analysis?${params.toString()}`);
    },
    generateReport: (tenantId, periodStart, periodEnd) => 
        api.get(`/vat/${tenantId}/report?period_start=${periodStart}&period_end=${periodEnd}`),
};

// Billing API
export const billingAPI = {
    getPlans: () => api.get('/billing/plans'),
    subscribe: (planId) => api.post('/billing/subscribe', { plan_id: planId }),
    getCurrentSubscription: () => api.get('/billing/subscription'),
    cancelSubscription: () => api.delete('/billing/subscription'),
};

// Dashboard API
export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats'),
    getAccountantOverview: () => api.get('/accountant/overview'),
};

// Admin API
export const adminAPI = {
    getUsers: () => api.get('/admin/users'),
    getStats: () => api.get('/admin/stats'),
    updateUserRole: (userId, role) => api.put(`/admin/users/${userId}/role?role=${role}`),
};

export default api;
