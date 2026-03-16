import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { User, Mail, Shield, Lock, Building, Link, CheckCircle, AlertCircle, RefreshCw, Unlink } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const PUBLIC_TOKEN = 'XMTQAfaSihOXVVi6WUwEB3yLmvn3BqIecYosMABmvis';

const authHeaders = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function SettingsPage() {
    const { user } = useAuth();
    const [passwordLoading, setPasswordLoading] = useState(false);
    const [econStatus, setEconStatus] = useState(null);
    const [econLoading, setEconLoading] = useState(false);
    const [syncing, setSyncing] = useState(false);

    useEffect(() => {
        checkEconomicStatus();
    }, []);

    const sendPasswordReset = async () => {
        setPasswordLoading(true);
        try {
            await axios.post(`${BACKEND_URL}/api/auth/password-reset/request`, { email: user.email });
            toast.success('Password reset link sent to ' + user.email);
        } catch {
            toast.error('Failed to send reset email');
        } finally {
            setPasswordLoading(false);
        }
    };

    const checkEconomicStatus = async () => {
        setEconLoading(true);
        try {
            const res = await axios.get(`${BACKEND_URL}/api/user/economic/status`, authHeaders());
            setEconStatus(res.data);
        } catch {
            setEconStatus({ connected: false });
        } finally {
            setEconLoading(false);
        }
    };

    const connectEconomic = () => {
        // Include user_id in callback URL so we can save the token
        const callbackUrl = encodeURIComponent(
            `${BACKEND_URL}/api/user/economic/callback?user_id=${user.id}`
        );
        const url = `https://secure.e-conomic.com/secure/api1/requestaccess.aspx?appPublicToken=${PUBLIC_TOKEN}&redirectUrl=${callbackUrl}`;
        window.open(url, '_blank');
        toast.info('Complete the connection in the e-conomic window, then click "Sync Clients" below.');
    };

    const syncClients = async () => {
        setSyncing(true);
        try {
            const res = await axios.post(`${BACKEND_URL}/api/user/economic/sync`, {}, authHeaders());
            if (res.data.success) {
                toast.success(`${res.data.synced} clients synced from e-conomic!`);
                checkEconomicStatus();
            } else {
                toast.error(res.data.message || 'Sync failed');
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Sync failed — make sure you completed the connection first');
        } finally {
            setSyncing(false);
        }
    };

    const testEconomic = async () => {
        setEconLoading(true);
        try {
            const res = await axios.get(`${BACKEND_URL}/api/user/economic/test`, authHeaders());
            if (res.data.success) {
                toast.success(res.data.message);
                setEconStatus(prev => ({ ...prev, connected: true }));
            } else {
                toast.error(res.data.error || 'Connection test failed');
            }
        } catch {
            toast.error('Test failed');
        } finally {
            setEconLoading(false);
        }
    };

    const disconnectEconomic = async () => {
        if (!window.confirm('Are you sure you want to disconnect e-conomic?')) return;
        try {
            await axios.delete(`${BACKEND_URL}/api/user/economic/disconnect`, authHeaders());
            setEconStatus({ connected: false });
            toast.success('E-conomic disconnected');
        } catch {
            toast.error('Failed to disconnect');
        }
    };

    return (
        <div className="space-y-8">
            <div>
                <h1 className="font-heading text-3xl font-bold">Settings</h1>
                <p className="text-muted-foreground mt-1">Manage your account and integrations</p>
            </div>

            {/* Profile */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><User className="h-5 w-5" />Profile</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-xl font-bold text-primary">{user?.name?.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                            <p className="font-semibold">{user?.name}</p>
                            <p className="text-sm text-muted-foreground">{user?.email}</p>
                            <Badge variant="secondary" className="mt-1">
                                <Shield className="h-3 w-3 mr-1" />{user?.role?.replace('_', ' ')}
                            </Badge>
                        </div>
                    </div>
                    <div className="grid gap-3 pt-3 border-t">
                        <div className="grid gap-1"><Label>Full Name</Label><Input value={user?.name || ''} disabled /></div>
                        <div className="grid gap-1"><Label>Email</Label><Input value={user?.email || ''} disabled /></div>
                    </div>
                </CardContent>
            </Card>

            {/* Password */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Lock className="h-5 w-5" />Password</CardTitle>
                    <CardDescription>We'll send a reset link to your email address</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">Reset link sent to {user?.email}</p>
                        <Button variant="outline" onClick={sendPasswordReset} disabled={passwordLoading}>
                            {passwordLoading ? 'Sending...' : 'Send Reset Link'}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* E-conomic Integration */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Building className="h-5 w-5" />E-conomic Integration
                    </CardTitle>
                    <CardDescription>
                        Connect YOUR e-conomic account to sync your clients into the Portfolio Dashboard
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">

                    {/* Status indicator */}
                    <div className={`flex items-center gap-3 p-3 rounded-lg ${
                        econStatus?.connected
                            ? 'bg-green-500/10 border border-green-500/20'
                            : 'bg-yellow-500/10 border border-yellow-500/20'
                    }`}>
                        {econStatus?.connected
                            ? <CheckCircle className="h-5 w-5 text-green-500" />
                            : <AlertCircle className="h-5 w-5 text-yellow-500" />}
                        <div>
                            <p className="text-sm font-medium">
                                {econStatus?.connected
                                    ? `Connected since ${econStatus.connected_at ? new Date(econStatus.connected_at).toLocaleDateString() : 'recently'}`
                                    : 'Not connected — connect your e-conomic to see real client data'}
                            </p>
                        </div>
                    </div>

                    {/* How it works */}
                    {!econStatus?.connected && (
                        <div className="bg-muted/50 rounded-lg p-4 text-sm text-muted-foreground space-y-1">
                            <p className="font-medium text-foreground">How it works:</p>
                            <p>1. Click "Connect E-conomic" below</p>
                            <p>2. Log in to e-conomic and click "Tilføj app"</p>
                            <p>3. Come back here and click "Sync Clients"</p>
                            <p>4. Your clients appear in the Portfolio Dashboard</p>
                        </div>
                    )}

                    {/* Action buttons */}
                    <div className="flex gap-3 flex-wrap">
                        {!econStatus?.connected ? (
                            <Button onClick={connectEconomic} className="flex items-center gap-2">
                                <Link className="h-4 w-4" />Connect E-conomic
                            </Button>
                        ) : (
                            <Button variant="outline" onClick={disconnectEconomic} className="flex items-center gap-2 text-red-500">
                                <Unlink className="h-4 w-4" />Disconnect
                            </Button>
                        )}

                        <Button variant="outline" onClick={syncClients} disabled={syncing} className="flex items-center gap-2">
                            <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
                            {syncing ? 'Syncing...' : 'Sync Clients'}
                        </Button>

                        <Button variant="ghost" size="sm" onClick={testEconomic} disabled={econLoading}>
                            {econLoading ? 'Testing...' : 'Test Connection'}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Account Info */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5" />Account Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-sm text-muted-foreground">Account ID</span>
                        <span className="text-sm font-mono">{user?.id?.slice(0, 8)}...</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-sm text-muted-foreground">Role</span>
                        <span className="text-sm">{user?.role?.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                        <span className="text-sm text-muted-foreground">Member since</span>
                        <span className="text-sm">
                            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
