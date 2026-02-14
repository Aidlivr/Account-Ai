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
    // Provider Configuration
    getProviderConfig: (tenantId) => api.get(`/tenants/${tenantId}/provider`),
    updateProviderConfig: (tenantId, config) => api.put(`/tenants/${tenantId}/provider`, config),
    testProviderConnection: (tenantId) => api.post(`/tenants/${tenantId}/provider/test`),
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
    editFields: (id, fieldUpdates) => api.put(`/documents/${id}/edit`, { field_updates: fieldUpdates }),
    approve: (id, approved, finalData = null, accountMapping = null) => 
        api.put(`/documents/${id}/approve`, { approved, final_data: finalData, account_mapping: accountMapping }),
};

// Voucher API
export const voucherAPI = {
    getAll: (tenantId, status = null) => {
        const params = status ? `?status=${status}` : '';
        return api.get(`/vouchers/${tenantId}${params}`);
    },
    getOne: (tenantId, voucherId) => api.get(`/vouchers/${tenantId}/${voucherId}`),
    push: (tenantId, voucherId) => api.post(`/vouchers/${tenantId}/push`, { voucher_id: voucherId }),
};

// Vendor API
export const vendorAPI = {
    getPatterns: (tenantId) => api.get(`/vendors/${tenantId}`),
    updatePattern: (tenantId, patternId, updates) => api.put(`/vendors/${tenantId}/${patternId}`, updates),
};

// Activity API
export const activityAPI = {
    getLogs: (tenantId, activityType = null, limit = 100) => {
        const params = new URLSearchParams();
        if (activityType) params.append('activity_type', activityType);
        params.append('limit', limit);
        return api.get(`/activity/${tenantId}?${params.toString()}`);
    },
    getTimeSaved: (tenantId, days = 30) => api.get(`/activity/${tenantId}/time-saved?days=${days}`),
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
    requestSubscription: (planId) => api.post(`/billing/request?plan_id=${planId}`),
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
    getSubscriptionRequests: () => api.get('/admin/subscription-requests'),
    activateSubscription: (userId, planId, notes = null) => 
        api.post('/admin/subscriptions/activate', { user_id: userId, plan_id: planId, notes }),
};

// Feedback API (Beta)
export const feedbackAPI = {
    submit: (data) => api.post('/feedback', data),
    getAll: () => api.get('/feedback'),
};

// Export API (Beta)
export const exportAPI = {
    exportVouchers: (tenantId, options = {}) => 
        api.post(`/export/${tenantId}/vouchers`, options, {
            responseType: options.format === 'csv' ? 'text' : 'json'
        }),
};

export default api;
