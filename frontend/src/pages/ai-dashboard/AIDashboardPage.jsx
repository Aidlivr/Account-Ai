import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, CheckCircle, Clock, Users, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../../components/ui/table';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../lib/api';

export default function AIDashboardPage() {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/ai-dashboard/stats');
            setStats(response.data);
        } catch (err) {
            setError('Failed to load AI statistics');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (user?.role !== 'admin' && user?.role !== 'accountant') {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <AlertTriangle className="h-12 w-12 text-warning mx-auto mb-4" />
                    <h2 className="text-xl font-semibold">Access Denied</h2>
                    <p className="text-muted-foreground">You need admin or accountant role to view this page</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
                    <p className="text-muted-foreground">{error}</p>
                </div>
            </div>
        );
    }

    const getAccuracyColor = (accuracy) => {
        if (accuracy >= 90) return 'text-success';
        if (accuracy >= 70) return 'text-warning';
        return 'text-destructive';
    };

    const getAccuracyBadge = (accuracy) => {
        if (accuracy >= 90) return <Badge variant="success">Excellent</Badge>;
        if (accuracy >= 70) return <Badge variant="warning">Good</Badge>;
        return <Badge variant="destructive">Needs Improvement</Badge>;
    };

    return (
        <div className="space-y-8" data-testid="ai-dashboard-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold flex items-center gap-3">
                        <Brain className="h-8 w-8 text-primary" />
                        AI Performance Dashboard
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Monitor AI extraction accuracy and vendor learning performance
                    </p>
                </div>
                {getAccuracyBadge(stats?.ai_accuracy_percent || 0)}
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                                <TrendingUp className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                                <p className={`text-3xl font-bold font-mono ${getAccuracyColor(stats?.ai_accuracy_percent)}`}>
                                    {stats?.ai_accuracy_percent?.toFixed(1) || 0}%
                                </p>
                                <p className="text-sm text-muted-foreground">Overall AI Accuracy</p>
                            </div>
                        </div>
                        <Progress 
                            value={stats?.ai_accuracy_percent || 0} 
                            className="mt-3 h-2"
                        />
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                <BarChart3 className="h-6 w-6 text-blue-500" />
                            </div>
                            <div>
                                <p className={`text-3xl font-bold font-mono ${getAccuracyColor(stats?.account_accuracy_percent)}`}>
                                    {stats?.account_accuracy_percent?.toFixed(1) || 0}%
                                </p>
                                <p className="text-sm text-muted-foreground">Account Accuracy</p>
                            </div>
                        </div>
                        <Progress 
                            value={stats?.account_accuracy_percent || 0} 
                            className="mt-3 h-2"
                        />
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                                <CheckCircle className="h-6 w-6 text-green-500" />
                            </div>
                            <div>
                                <p className={`text-3xl font-bold font-mono ${getAccuracyColor(stats?.vat_accuracy_percent)}`}>
                                    {stats?.vat_accuracy_percent?.toFixed(1) || 0}%
                                </p>
                                <p className="text-sm text-muted-foreground">VAT Accuracy</p>
                            </div>
                        </div>
                        <Progress 
                            value={stats?.vat_accuracy_percent || 0} 
                            className="mt-3 h-2"
                        />
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                <Clock className="h-6 w-6 text-amber-500" />
                            </div>
                            <div>
                                <p className="text-3xl font-bold font-mono text-amber-600">
                                    {stats?.time_saved_hours?.toFixed(1) || 0}h
                                </p>
                                <p className="text-sm text-muted-foreground">Time Saved</p>
                            </div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-3">
                            ~{stats?.time_saved_estimate_per_invoice_minutes || 5} min per invoice
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Secondary Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                            <Brain className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{stats?.total_extractions || 0}</p>
                            <p className="text-sm text-muted-foreground">Total Extractions</p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                            <TrendingUp className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">
                                {stats?.average_confidence_score?.toFixed(2) || 0}
                            </p>
                            <p className="text-sm text-muted-foreground">Avg Confidence Score</p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center">
                            <AlertTriangle className="h-5 w-5 text-destructive" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono text-destructive">
                                {stats?.error_rate_percent?.toFixed(1) || 0}%
                            </p>
                            <p className="text-sm text-muted-foreground">Error Rate</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Most Corrected Accounts */}
            {stats?.most_corrected_accounts?.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-warning" />
                            Most Corrected Accounts
                        </CardTitle>
                        <CardDescription>
                            Accounts where AI suggestions are frequently overridden
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Account Code</TableHead>
                                    <TableHead className="text-right">Corrections</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {stats.most_corrected_accounts.map((item, idx) => (
                                    <TableRow key={idx}>
                                        <TableCell className="font-mono">{item.account || 'N/A'}</TableCell>
                                        <TableCell className="text-right">
                                            <Badge variant="outline">{item.corrections}</Badge>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}

            {/* Vendor Accuracy */}
            {stats?.vendor_accuracy?.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Users className="h-5 w-5 text-primary" />
                            Vendor Accuracy
                        </CardTitle>
                        <CardDescription>
                            AI accuracy per vendor (based on correction history)
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Vendor</TableHead>
                                    <TableHead className="text-right">Total</TableHead>
                                    <TableHead className="text-right">Accuracy</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {stats.vendor_accuracy.slice(0, 10).map((vendor, idx) => (
                                    <TableRow key={idx}>
                                        <TableCell className="font-medium">{vendor.vendor}</TableCell>
                                        <TableCell className="text-right font-mono">{vendor.total}</TableCell>
                                        <TableCell className="text-right">
                                            <span className={getAccuracyColor(vendor.accuracy)}>
                                                {vendor.accuracy.toFixed(1)}%
                                            </span>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}

            {/* No Data State */}
            {stats?.total_extractions === 0 && (
                <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No AI Data Yet</h3>
                        <p className="text-muted-foreground text-center max-w-md">
                            Process some invoices to start collecting AI performance metrics.
                            The dashboard will show accuracy, vendor learning, and time savings.
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
