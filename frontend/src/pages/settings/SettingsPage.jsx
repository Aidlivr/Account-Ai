import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { User, Mail, Shield, Lock, Building, Link, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function SettingsPage() {
    const { user } = useAuth();
    const [passwordLoading, setPasswordLoading] = useState(false);
    const [econStatus, setEconStatus] = useState(null);
    const [econLoading, setEconLoading] = useState(false);
    const [econChecked, setEconChecked] = useState(false);

    const sendPasswordReset = async () => {
        setPasswordLoading(true);
        try {
            await axios.post(`${BACKEND_URL}/api/auth/password-reset/request`, { email: user.email });
            toast.success('Password reset link sent to ' + user.email);
        } catch (err) {
            toast.error('Failed to send reset email');
        } finally {
            setPasswordLoading(false);
        }
    };

    const testEconomic = async () => {
        setEconLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${BACKEND_URL}/api/test/economic`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setEconStatus(res.data);
            setEconChecked(true);
            if (res.data.success) {
                toast.success(`Connected! ${res.data.accounts_count} accounts found.`);
            } else {
                toast.error(res.data.error || 'Connection failed');
            }
        } catch (err) {
            toast.error('E-conomic test failed');
        } finally {
            setEconLoading(false);
        }
    };

    const connectEconomic = () => {
        const publicToken = 'XMTQAfaSihOXVVi6WUwEB3yLmvn3BqIecYosMABmvis';
        const callbackUrl = encodeURIComponent(`https://accountrix.norabot.ai/api/economic/callback`);
        const url = `https://secure.e-conomic.com/secure/api1/requestaccess.aspx?appPublicToken=${publicToken}&redirectUrl=${callbackUrl}`;
        window.open(url, '_blank');
    };

    return (
        <div className="space-y-8" data-testid="settings-page">
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
                        <div className="grid gap-1"><Label>Member since</Label><Input value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''} disabled /></div>
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
                        <p className="text-sm text-muted-foreground">Reset link will be sent to {user?.email}</p>
                        <Button variant="outline" onClick={sendPasswordReset} disabled={passwordLoading}>
                            {passwordLoading ? 'Sending...' : 'Send Reset Link'}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* E-conomic */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Building className="h-5 w-5" />E-conomic Integration</CardTitle>
                    <CardDescription>Connect your e-conomic account to sync real accounting data</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {econChecked && econStatus && (
                        <div className={`flex items-center gap-3 p-3 rounded-lg ${econStatus.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                            {econStatus.success
                                ? <CheckCircle className="h-5 w-5 text-green-500" />
                                : <AlertCircle className="h-5 w-5 text-red-500" />}
                            <p className="text-sm font-medium">
                                {econStatus.success ? `Connected — ${econStatus.accounts_count} accounts` : econStatus.error}
                            </p>
                        </div>
                    )}
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={testEconomic} disabled={econLoading}>
                            {econLoading ? 'Testing...' : 'Test Connection'}
                        </Button>
                        <Button onClick={connectEconomic} className="flex items-center gap-2">
                            <Link className="h-4 w-4" />Connect E-conomic
                        </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Clicking Connect opens e-conomic's authorization page. After granting access your data syncs automatically.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
