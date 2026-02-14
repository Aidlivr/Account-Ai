import React, { useState, useEffect } from 'react';
import { Users, Building2, FileText, CreditCard, Shield, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import { adminAPI } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
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
import { toast } from 'sonner';
import { formatDate } from '../../lib/utils';

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
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, usersRes] = await Promise.all([
                    adminAPI.getStats(),
                    adminAPI.getUsers()
                ]);
                setStats(statsRes.data);
                setUsers(usersRes.data);
            } catch (err) {
                console.error('Failed to fetch admin data:', err);
                toast.error('Failed to load admin data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleRoleChange = async (userId, newRole) => {
        try {
            await adminAPI.updateUserRole(userId, newRole);
            setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
            toast.success('User role updated');
        } catch (err) {
            toast.error('Failed to update role');
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
                className="grid grid-cols-1 md:grid-cols-4 gap-4"
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
                                <p className="text-sm text-muted-foreground">Total Users</p>
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

            {/* Users Table */}
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
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
