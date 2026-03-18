import React, { useState, useEffect } from 'react';
import { Users, Building2, FileText, CreditCard, Shield, CheckCircle, Clock, TrendingUp, RefreshCw, AlertCircle } from 'lucide-react';
import { adminAPI, billingAPI } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { formatDate } from '../../lib/utils';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = (path) => axios.get(`${BACKEND_URL}/api${path}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function AdminPanel() {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [plans, setPlans] = useState([]);
    const [subscriptionRequests, setSubscriptionRequests] = useState([]);
    const [revenue, setRevenue] = useState(null);
    const [pendingUsers, setPendingUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isActivateOpen, setIsActivateOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedPlan, setSelectedPlan] = useState('');
    const [activationNotes, setActivationNotes] = useState('');
    const [activating, setActivating] = useState(false);

    useEffect(() => { fetchData(); }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statsRes, usersRes, plansRes, requestsRes, revenueRes, pendingRes] = await Promise.all([
                adminAPI.getStats(),
                api('/admin/users/detailed'),
                billingAPI.getPlans(),
                adminAPI.getSubscriptionRequests(),
                api('/admin/revenue'),
                api('/admin/users/pending'),
            ]);
            setStats(statsRes.data);
            setUsers(usersRes.data);
            setPlans(plansRes.data);
            setSubscriptionRequests(requestsRes.data);
            setRevenue(revenueRes.data);
            setPendingUsers(pendingRes.data || []);
        } catch (err) {
            console.error(err);
            toast.error('Failed to load admin data');
        } finally {
            setLoading(false);
        }
    };

    const handleRoleChange = async (userId, newRole) => {
        try {
            await adminAPI.updateUserRole(userId, newRole);
            setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
            toast.success('Role updated');
        } catch { toast.error('Failed to update role'); }
    };

    const approveUser = async (userId, userEmail) => {
        try {
            await axios.post(`${BACKEND_URL}/api/admin/users/${userId}/approve`, {}, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            toast.success(`${userEmail} approved!`);
            fetchData();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to approve');
        }
    };

    const rejectUser = async (userId, userEmail) => {
        if (!window.confirm(`Reject ${userEmail}?`)) return;
        try {
            await axios.post(`${BACKEND_URL}/api/admin/users/${userId}/reject`, {}, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            toast.success(`${userEmail} rejected`);
            fetchData();
        } catch (err) {
            toast.error('Failed to reject');
        }
    };

    const openActivateDialog = (user) => {
        setSelectedUser(user);
        setSelectedPlan('');
        setActivationNotes('');
        setIsActivateOpen(true);
    };

    const handleActivateSubscription = async () => {
        if (!selectedPlan) { toast.error('Please select a plan'); return; }
        setActivating(true);
        try {
            await adminAPI.activateSubscription(selectedUser.id, selectedPlan, activationNotes || null);
            toast.success('Subscription activated!');
            setIsActivateOpen(false);
            fetchData();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Activation failed');
        } finally { setActivating(false); }
    };

    if (loading) return (
        <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
    );

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Admin Panel</h1>
                    <p className="text-muted-foreground mt-1">User management, subscriptions and revenue</p>
                </div>
                <Button variant="outline" size="sm" onClick={fetchData}>
                    <RefreshCw className="h-4 w-4 mr-2" />Refresh
                </Button>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Users className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{stats?.total_users || 0}</p>
                            <p className="text-xs text-muted-foreground">Total Users</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                            <CreditCard className="h-5 w-5 text-green-500" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{stats?.active_subscriptions || 0}</p>
                            <p className="text-xs text-muted-foreground">Active Subs</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <Building2 className="h-5 w-5 text-blue-500" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{stats?.total_portfolio_clients || 0}</p>
                            <p className="text-xs text-muted-foreground">Portfolio Clients</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                            <TrendingUp className="h-5 w-5 text-yellow-500" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">
                                {revenue ? `${revenue.mrr_dkk.toLocaleString()}` : '0'}
                            </p>
                            <p className="text-xs text-muted-foreground">MRR (DKK)</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Revenue card */}
            {revenue && (
                <Card className="border-yellow-500/20 bg-yellow-500/5">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-base">
                            <TrendingUp className="h-4 w-4" />Revenue Overview
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-xs text-muted-foreground">Monthly Recurring</p>
                            <p className="text-xl font-bold font-mono">{revenue.mrr_dkk.toLocaleString()} DKK</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Annual Recurring</p>
                            <p className="text-xl font-bold font-mono">{revenue.arr_dkk.toLocaleString()} DKK</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Professional Plans</p>
                            <p className="text-xl font-bold font-mono">{revenue.professional_count}</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Enterprise Plans</p>
                            <p className="text-xl font-bold font-mono">{revenue.enterprise_count}</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Tabs */}
            <Tabs defaultValue="users" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="pending">
                        Pending Approval
                        {pendingUsers.length > 0 && (
                            <Badge variant="destructive" className="ml-2">{pendingUsers.length}</Badge>
                        )}
                    </TabsTrigger>
                    <TabsTrigger value="users">Users & Clients</TabsTrigger>
                    <TabsTrigger value="subscriptions">
                        Subscriptions
                        {stats?.pending_subscription_requests > 0 && (
                            <Badge variant="destructive" className="ml-2">{stats.pending_subscription_requests}</Badge>
                        )}
                    </TabsTrigger>
                </TabsList>

                {/* Pending Approval Tab */}
                <TabsContent value="pending">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Clock className="h-5 w-5 text-yellow-500" />Pending Approvals
                            </CardTitle>
                            <CardDescription>
                                Accountants waiting for your approval before they can log in
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-0">
                            {pendingUsers.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-16">
                                    <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                                    <p className="text-muted-foreground">No pending approvals</p>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Name</TableHead>
                                            <TableHead>Firm / CVR</TableHead>
                                            <TableHead>Email</TableHead>
                                            <TableHead>Phone</TableHead>
                                            <TableHead>Registered</TableHead>
                                            <TableHead>Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {pendingUsers.map((user) => (
                                            <TableRow key={user.id}>
                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-7 h-7 rounded-full bg-yellow-500/10 flex items-center justify-center text-xs font-bold text-yellow-500">
                                                            {user.name?.charAt(0).toUpperCase()}
                                                        </div>
                                                        <span className="font-medium text-sm">{user.name}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <p className="text-sm font-medium">{user.firm_name || '—'}</p>
                                                    <p className="text-xs text-muted-foreground">CVR: {user.cvr_number || '—'}</p>
                                                </TableCell>
                                                <TableCell className="text-sm text-muted-foreground">{user.email}</TableCell>
                                                <TableCell className="text-sm text-muted-foreground">{user.phone || '—'}</TableCell>
                                                <TableCell className="text-xs text-muted-foreground">{formatDate(user.created_at)}</TableCell>
                                                <TableCell>
                                                    <div className="flex gap-2">
                                                        <Button size="sm" className="h-7 text-xs bg-green-600 hover:bg-green-500"
                                                            onClick={() => approveUser(user.id, user.email)}>
                                                            ✓ Approve
                                                        </Button>
                                                        <Button size="sm" variant="outline" className="h-7 text-xs text-red-500 border-red-500/20"
                                                            onClick={() => rejectUser(user.id, user.email)}>
                                                            ✗ Reject
                                                        </Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Users Tab */}
                <TabsContent value="users">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Users className="h-5 w-5" />User Management
                            </CardTitle>
                            <CardDescription>
                                Each accountant's client count and monthly billing
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>User</TableHead>
                                        <TableHead>Role</TableHead>
                                        <TableHead>Clients</TableHead>
                                        <TableHead>Monthly Cost</TableHead>
                                        <TableHead>Subscription</TableHead>
                                        <TableHead>Joined</TableHead>
                                        <TableHead>Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {users.map((user) => (
                                        <TableRow key={user.id}>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                                                        {user.name?.charAt(0).toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-sm">{user.name}</p>
                                                        <p className="text-xs text-muted-foreground">{user.email}</p>
                                                    </div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Select value={user.role} onValueChange={(v) => handleRoleChange(user.id, v)}>
                                                    <SelectTrigger className="w-32 h-7 text-xs">
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="sme_user">SME User</SelectItem>
                                                        <SelectItem value="accountant">Accountant</SelectItem>
                                                        <SelectItem value="admin">Admin</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-1">
                                                    <Building2 className="h-3 w-3 text-muted-foreground" />
                                                    <span className="font-mono font-bold">{user.client_count}</span>
                                                    {user.client_count > 100 && (
                                                        <Badge variant="outline" className="text-xs ml-1">+{user.client_count - 100} extra</Badge>
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <span className="font-mono text-sm">
                                                    {user.monthly_cost_dkk > 0 ? `${user.monthly_cost_dkk.toLocaleString()} DKK` : '—'}
                                                </span>
                                            </TableCell>
                                            <TableCell>
                                                {user.subscription_status === 'active' ? (
                                                    <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
                                                        <CheckCircle className="h-3 w-3 mr-1" />{user.subscription_plan}
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="outline" className="text-muted-foreground">
                                                        <AlertCircle className="h-3 w-3 mr-1" />No plan
                                                    </Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="text-xs text-muted-foreground">
                                                {formatDate(user.created_at)}
                                            </TableCell>
                                            <TableCell>
                                                <Button size="sm" variant="outline" className="h-7 text-xs" onClick={() => openActivateDialog(user)}>
                                                    {user.subscription_status === 'active' ? 'Change Plan' : 'Activate'}
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Subscriptions Tab */}
                <TabsContent value="subscriptions">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <CreditCard className="h-5 w-5" />Subscription Requests
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                            {subscriptionRequests.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-16">
                                    <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                                    <p className="text-muted-foreground">No pending requests</p>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>User</TableHead>
                                            <TableHead>Plan</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Requested</TableHead>
                                            <TableHead>Action</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {subscriptionRequests.map((req) => (
                                            <TableRow key={req.id}>
                                                <TableCell>
                                                    <p className="font-medium text-sm">{req.user_name}</p>
                                                    <p className="text-xs text-muted-foreground">{req.user_email}</p>
                                                </TableCell>
                                                <TableCell><Badge variant="outline">{req.plan_id}</Badge></TableCell>
                                                <TableCell>
                                                    {req.status === 'pending' ? (
                                                        <Badge variant="warning"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
                                                    ) : (
                                                        <Badge variant="success"><CheckCircle className="h-3 w-3 mr-1" />Approved</Badge>
                                                    )}
                                                </TableCell>
                                                <TableCell className="text-xs text-muted-foreground">{formatDate(req.requested_at)}</TableCell>
                                                <TableCell>
                                                    {req.status === 'pending' && (
                                                        <Button size="sm" className="h-7 text-xs" onClick={() => {
                                                            setSelectedUser({ id: req.user_id, email: req.user_email });
                                                            setSelectedPlan(req.plan_id);
                                                            setIsActivateOpen(true);
                                                        }}>Activate</Button>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Activate Dialog */}
            <Dialog open={isActivateOpen} onOpenChange={setIsActivateOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Activate Subscription</DialogTitle>
                        <DialogDescription>Manually activate for {selectedUser?.email}</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Plan</Label>
                            <Select value={selectedPlan} onValueChange={setSelectedPlan}>
                                <SelectTrigger><SelectValue placeholder="Choose a plan" /></SelectTrigger>
                                <SelectContent>
                                    {plans.map((plan) => (
                                        <SelectItem key={plan.id} value={plan.id}>
                                            {plan.name} — {plan.price} {plan.currency?.toUpperCase()}/mo
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label>Notes (optional)</Label>
                            <Input placeholder="e.g. Beta tester, free trial..." value={activationNotes} onChange={(e) => setActivationNotes(e.target.value)} />
                        </div>
                        {selectedPlan === 'professional' && (
                            <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 text-sm">
                                <p className="font-medium">Professional Plan</p>
                                <p className="text-muted-foreground text-xs mt-1">2,499 DKK/month — up to 100 clients, +15 DKK per extra client</p>
                            </div>
                        )}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsActivateOpen(false)}>Cancel</Button>
                        <Button onClick={handleActivateSubscription} disabled={activating || !selectedPlan}>
                            {activating ? 'Activating...' : 'Activate'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
