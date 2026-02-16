import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { TenantProvider } from "./contexts/TenantContext";
import { MainLayout } from "./components/layout/MainLayout";
import { Toaster } from "./components/ui/sonner";

// Landing Page
import LandingPage from "./pages/landing/LandingPage";

// Auth Pages
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";

// Main Pages
import DashboardPage from "./pages/dashboard/DashboardPage";
import CompaniesPage from "./pages/companies/CompaniesPage";
import DocumentsPage from "./pages/documents/DocumentsPage";
import VouchersPage from "./pages/vouchers/VouchersPage";
import ReconciliationPage from "./pages/reconciliation/ReconciliationPage";
import VATPage from "./pages/vat/VATPage";
import ActivityPage from "./pages/activity/ActivityPage";
import BillingPage from "./pages/billing/BillingPage";
import AccountantDashboard from "./pages/accountant/AccountantDashboard";
import AdminPanel from "./pages/admin/AdminPanel";
import SettingsPage from "./pages/settings/SettingsPage";
import AIDashboardPage from "./pages/ai-dashboard/AIDashboardPage";

function App() {
    return (
        <AuthProvider>
            <TenantProvider>
                <BrowserRouter>
                    <Routes>
                        {/* Public Routes */}
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />

                        {/* Protected Routes */}
                        <Route path="/app" element={<MainLayout />}>
                            <Route index element={<Navigate to="/app/dashboard" replace />} />
                            <Route path="dashboard" element={<DashboardPage />} />
                            <Route path="companies" element={<CompaniesPage />} />
                            <Route path="documents" element={<DocumentsPage />} />
                            <Route path="vouchers" element={<VouchersPage />} />
                            <Route path="reconciliation" element={<ReconciliationPage />} />
                            <Route path="vat" element={<VATPage />} />
                            <Route path="activity" element={<ActivityPage />} />
                            <Route path="billing" element={<BillingPage />} />
                            <Route path="accountant" element={<AccountantDashboard />} />
                            <Route path="admin" element={<AdminPanel />} />
                            <Route path="ai-dashboard" element={<AIDashboardPage />} />
                            <Route path="settings" element={<SettingsPage />} />
                        </Route>

                        {/* Legacy routes - redirect to /app */}
                        <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
                        <Route path="/companies" element={<Navigate to="/app/companies" replace />} />
                        <Route path="/documents" element={<Navigate to="/app/documents" replace />} />
                        <Route path="/vouchers" element={<Navigate to="/app/vouchers" replace />} />
                        <Route path="/reconciliation" element={<Navigate to="/app/reconciliation" replace />} />
                        <Route path="/vat" element={<Navigate to="/app/vat" replace />} />
                        <Route path="/activity" element={<Navigate to="/app/activity" replace />} />
                        <Route path="/billing" element={<Navigate to="/app/billing" replace />} />
                        <Route path="/accountant" element={<Navigate to="/app/accountant" replace />} />
                        <Route path="/admin" element={<Navigate to="/app/admin" replace />} />
                        <Route path="/ai-dashboard" element={<Navigate to="/app/ai-dashboard" replace />} />
                        <Route path="/settings" element={<Navigate to="/app/settings" replace />} />

                        {/* Catch all */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </BrowserRouter>
                <Toaster position="top-right" richColors />
            </TenantProvider>
        </AuthProvider>
    );
}

export default App;
