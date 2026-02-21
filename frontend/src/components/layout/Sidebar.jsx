import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
    LayoutDashboard, 
    Building2, 
    FileText, 
    ArrowLeftRight, 
    Calculator, 
    CreditCard,
    Users,
    Settings,
    LogOut,
    ChevronDown,
    UsersRound,
    Brain,
    Shield,
    Bell,
    Clock
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTenant } from '../../contexts/TenantContext';
import { Button } from '../ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    DropdownMenuSeparator,
} from '../ui/dropdown-menu';
import { cn } from '../../lib/utils';

// Portfolio Risk Platform - Primary Navigation
const portfolioItems = [
    { to: '/app/portfolio', icon: Shield, label: 'Risk Dashboard' },
    { to: '/app/portfolio/exceptions', icon: Bell, label: 'Exception Inbox' },
    { to: '/app/portfolio/pre-vat', icon: Clock, label: 'Pre-VAT Review' },
];

// Legacy/Secondary Navigation
const navItems = [
    { to: '/app/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { to: '/app/companies', icon: Building2, label: 'Companies' },
    { to: '/app/documents', icon: FileText, label: 'Documents' },
    { to: '/app/vouchers', icon: FileText, label: 'Vouchers' },
    { to: '/app/reconciliation', icon: ArrowLeftRight, label: 'Reconciliation' },
    { to: '/app/vat', icon: Calculator, label: 'VAT Analysis' },
    { to: '/app/activity', icon: Users, label: 'Activity Log' },
    { to: '/app/billing', icon: CreditCard, label: 'Billing' },
];

const accountantItems = [
    { to: '/app/accountant', icon: UsersRound, label: 'Client Overview' },
    { to: '/app/ai-dashboard', icon: Brain, label: 'AI Performance' },
];

const adminItems = [
    { to: '/app/admin', icon: Users, label: 'Admin Panel' },
    { to: '/app/ai-dashboard', icon: Brain, label: 'AI Dashboard' },
];

export const Sidebar = () => {
    const { user, logout, isAccountant, isAdmin } = useAuth();
    const { tenants, currentTenant, selectTenant } = useTenant();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border/60 bg-card/50 backdrop-blur-xl flex flex-col z-50" data-testid="sidebar">
            {/* Logo */}
            <div className="p-6 border-b border-border/60">
                <h1 className="font-heading text-xl font-bold text-primary">
                    AI Copilot
                </h1>
                <p className="text-xs text-muted-foreground mt-1">Accounting Assistant</p>
            </div>

            {/* Tenant Selector */}
            {tenants.length > 0 && (
                <div className="p-4 border-b border-border/60">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="w-full justify-between" data-testid="tenant-selector">
                                <span className="truncate">{currentTenant?.name || 'Select Company'}</span>
                                <ChevronDown className="h-4 w-4 ml-2 shrink-0 opacity-50" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56" align="start">
                            {tenants.map((tenant) => (
                                <DropdownMenuItem
                                    key={tenant.id}
                                    onClick={() => selectTenant(tenant)}
                                    className={cn(
                                        "cursor-pointer",
                                        currentTenant?.id === tenant.id && "bg-primary/10"
                                    )}
                                    data-testid={`tenant-option-${tenant.id}`}
                                >
                                    <Building2 className="h-4 w-4 mr-2" />
                                    {tenant.name}
                                </DropdownMenuItem>
                            ))}
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => navigate('/companies')} className="cursor-pointer">
                                <Settings className="h-4 w-4 mr-2" />
                                Manage Companies
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            )}

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto p-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => cn("sidebar-link", isActive && "active")}
                        data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                    >
                        <item.icon className="h-5 w-5" />
                        <span>{item.label}</span>
                    </NavLink>
                ))}

                {isAccountant && (
                    <>
                        <div className="pt-4 pb-2">
                            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3">
                                Accountant
                            </span>
                        </div>
                        {accountantItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) => cn("sidebar-link", isActive && "active")}
                                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                            >
                                <item.icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </>
                )}

                {isAdmin && (
                    <>
                        <div className="pt-4 pb-2">
                            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3">
                                Admin
                            </span>
                        </div>
                        {adminItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) => cn("sidebar-link", isActive && "active")}
                                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                            >
                                <item.icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </>
                )}
            </nav>

            {/* User Menu */}
            <div className="p-4 border-t border-border/60">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="w-full justify-start" data-testid="user-menu">
                            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                                <span className="text-sm font-medium text-primary">
                                    {user?.name?.charAt(0).toUpperCase()}
                                </span>
                            </div>
                            <div className="flex-1 text-left">
                                <p className="text-sm font-medium truncate">{user?.name}</p>
                                <p className="text-xs text-muted-foreground capitalize">{user?.role?.replace('_', ' ')}</p>
                            </div>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuItem onClick={() => navigate('/settings')} className="cursor-pointer">
                            <Settings className="h-4 w-4 mr-2" />
                            Settings
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-destructive" data-testid="logout-btn">
                            <LogOut className="h-4 w-4 mr-2" />
                            Logout
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </aside>
    );
};
