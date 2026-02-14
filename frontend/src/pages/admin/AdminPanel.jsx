import React, { useState, useEffect } from 'react';
import { Users, Building2, FileText, CreditCard, Shield, Receipt, CheckCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { adminAPI, billingAPI } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../../components/ui/table';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../../components/ui/select';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { formatDate, formatDateTime } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function AdminPanel() {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [plans, setPlans] = useState([]);
    const [subscriptionRequests, setSubscriptionRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isActivateOpen, setIsActivateOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedPlan, setSelectedPlan] = useState('');
    const [activationNotes, setActivationNotes] = useState('');
    const [activating, setActivating] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, usersRes, plansRes, requestsRes] = await Promise.all([
                adminAPI.getStats(),
                adminAPI.getUsers(),
                billingAPI.getPlans(),
                adminAPI.getSubscriptionRequests()
            ]);
            setStats(statsRes.data);
            setUsers(usersRes.data);
            setPlans(plansRes.data);
            setSubscriptionRequests(requestsRes.data);
        } catch (err) {
            console.error('Failed to fetch admin data:', err);
            toast.error('Failed to load admin data');
        } finally {
            setLoading(false);
        }
    };

    const handleRoleChange = async (userId, newRole) => {
        try {
            await adminAPI.updateUserRole(userId, newRole);
            setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
            toast.success('User role updated');
        } catch (err) {
            toast.error('Failed to update role');
        }
    };

    const openActivateDialog = (user) => {
        setSelectedUser(user);
        setSelectedPlan('');
        setActivationNotes('');
        setIsActivateOpen(true);
    };

    const handleActivateSubscription = async () => {
        if (!selectedPlan) {
            toast.error('Please select a plan');
            return;
        }

        setActivating(true);
        try {
            await adminAPI.activateSubscription(selectedUser.id, selectedPlan, activationNotes || null);
            toast.success('Subscription activated successfully');
            setIsActivateOpen(false);
            fetchData();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Activation failed');
        } finally {
            setActivating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-16">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8" data-testid="admin-panel">
            {/* Header */}
            <div>
                <h1 className="font-heading text-3xl font-bold">Admin Panel</h1>
                <p className="text-muted-foreground mt-1">
                    System administration and user management
                </p>
            </div>

            {/* Stats */}
            <motion.div 
                className="grid grid-cols-1 md:grid-cols-5 gap-4"
                variants={container}
                initial="hidden"
                animate="show"
            >
                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                <Users className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{stats?.total_users || 0}</p>
                                <p className="text-sm text-muted-foreground">Users</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-info/10 flex items-center justify-center">
                                <Building2 className="h-5 w-5 text-info" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{stats?.total_tenants || 0}</p>
                                <p className="text-sm text-muted-foreground">Companies</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                                <FileText className="h-5 w-5 text-success" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{stats?.total_documents || 0}</p>
                                <p className="text-sm text-muted-foreground">Documents</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                                <Receipt className="h-5 w-5 text-accent" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{stats?.total_vouchers || 0}</p>
                                <p className="text-sm text-muted-foreground">Vouchers</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                                <CreditCard className="h-5 w-5 text-warning" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{stats?.active_subscriptions || 0}</p>
                                <p className="text-sm text-muted-foreground">Active Subs</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            </motion.div>

            {/* Tabs */}
            <Tabs defaultValue="users" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="users">Users</TabsTrigger>
                    <TabsTrigger value="subscriptions">
                        Subscriptions
                        {stats?.pending_subscription_requests > 0 && (
                            <Badge variant="destructive" className="ml-2">{stats.pending_subscription_requests}</Badge>
                        )}
                    </TabsTrigger>
                </TabsList>

                {/* Users Tab */}
                <TabsContent value="users">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Users className="h-5 w-5" />
                                User Management
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow className="data-table-header">
                                        <TableHead>User</TableHead>
                                        <TableHead>Email</TableHead>
                                        <TableHead>Role</TableHead>
                                        <TableHead>Joined</TableHead>
                                        <TableHead className="w-48">Change Role</TableHead>
                                        <TableHead className="w-32">Subscription</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {users.map((user) => (
                                        <TableRow key={user.id} className="data-table-row">
                                            <TableCell className="data-table-cell">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                                        <span className="text-sm font-medium text-primary">
                                                            {user.name?.charAt(0).toUpperCase()}
                                                        </span>
                                                    </div>
                                                    <span className="font-medium">{user.name}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="data-table-cell text-muted-foreground">
                                                {user.email}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Badge 
                                                    variant={
                                                        user.role === 'admin' ? 'default' : 
                                                        user.role === 'accountant' ? 'secondary' : 'outline'
                                                    }
                                                >
                                                    {user.role === 'admin' && <Shield className="h-3 w-3 mr-1" />}
                                                    {user.role?.replace('_', ' ')}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="data-table-cell text-muted-foreground">
                                                {formatDate(user.created_at)}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Select 
                                                    value={user.role} 
                                                    onValueChange={(value) => handleRoleChange(user.id, value)}
                                                >
                                                    <SelectTrigger className="w-36" data-testid={`role-select-${user.id}`}>
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="sme_user">SME User</SelectItem>
                                                        <SelectItem value="accountant">Accountant</SelectItem>
                                                        <SelectItem value="admin">Admin</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Button 
                                                    size="sm" 
                                                    variant="outline"
                                                    onClick={() => openActivateDialog(user)}
                                                    data-testid={`activate-sub-${user.id}`}
                                                >
                                                    Activate
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
                                <CreditCard className="h-5 w-5" />
                                Subscription Requests
                            </CardTitle>
                            <CardDescription>
                                Pending subscription requests awaiting activation
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-0">
                            {subscriptionRequests.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-16">
                                    <CheckCircle className="h-12 w-12 text-success mb-4" />
                                    <p className="text-muted-foreground">No pending requests</p>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow className="data-table-header">
                                            <TableHead>User</TableHead>
                                            <TableHead>Email</TableHead>
                                            <TableHead>Plan Requested</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Requested At</TableHead>
                                            <TableHead className="w-32">Action</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {subscriptionRequests.map((request) => (
                                            <TableRow key={request.id} className="data-table-row">
                                                <TableCell className="data-table-cell font-medium">
                                                    {request.user_name}
                                                </TableCell>
                                                <TableCell className="data-table-cell text-muted-foreground">
                                                    {request.user_email}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    <Badge variant="outline">{request.plan_id}</Badge>
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    {request.status === 'pending' ? (
                                                        <Badge variant="warning">
                                                            <Clock className="h-3 w-3 mr-1" /> Pending
                                                        </Badge>
                                                    ) : (
                                                        <Badge variant="success">
                                                            <CheckCircle className="h-3 w-3 mr-1" /> Approved
                                                        </Badge>
                                                    )}
                                                </TableCell>
                                                <TableCell className="data-table-cell text-muted-foreground">
                                                    {formatDateTime(request.requested_at)}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    {request.status === 'pending' && (
                                                        <Button 
                                                            size="sm"
                                                            onClick={() => {
                                                                setSelectedUser({ id: request.user_id, email: request.user_email });
                                                                setSelectedPlan(request.plan_id);
                                                                setIsActivateOpen(true);
                                                            }}
                                                        >
                                                            Activate
                                                        </Button>
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

            {/* Activate Subscription Dialog */}
            <Dialog open={isActivateOpen} onOpenChange={setIsActivateOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Activate Subscription</DialogTitle>
                        <DialogDescription>
                            Manually activate a subscription for {selectedUser?.email}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Select Plan</Label>
                            <Select value={selectedPlan} onValueChange={setSelectedPlan}>
                                <SelectTrigger data-testid="plan-select">
                                    <SelectValue placeholder="Choose a plan" />
                                </SelectTrigger>
                                <SelectContent>
                                    {plans.map((plan) => (
                                        <SelectItem key={plan.id} value={plan.id}>
                                            {plan.name} - {plan.price} {plan.currency.toUpperCase()}/mo
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label>Activation Notes (optional)</Label>
                            <Input
                                placeholder="e.g., Beta tester, free trial..."
                                value={activationNotes}
                                onChange={(e) => setActivationNotes(e.target.value)}
                                data-testid="activation-notes"
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsActivateOpen(false)}>
                            Cancel
                        </Button>
                        <Button 
                            onClick={handleActivateSubscription} 
                            disabled={activating || !selectedPlan}
                            data-testid="confirm-activate-btn"
                        >
                            {activating ? 'Activating...' : 'Activate Subscription'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
