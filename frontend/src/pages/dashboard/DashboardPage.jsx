import React, { useState, useEffect } from 'react';
import { 
    FileText, 
    Clock, 
    CheckCircle, 
    AlertTriangle, 
    ArrowLeftRight, 
    TrendingUp,
    Upload
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { dashboardAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { getRiskLevel } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.1 }
    }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function DashboardPage() {
    const { currentTenant } = useTenant();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await dashboardAPI.getStats();
                setStats(response.data);
            } catch (err) {
                console.error('Failed to fetch stats:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [currentTenant]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    const riskInfo = getRiskLevel(stats?.vat_risk_score || 0);

    return (
        <div className="space-y-8" data-testid="dashboard-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">
                        {currentTenant ? `Overview for ${currentTenant.name}` : 'Welcome to AI Accounting Copilot'}
                    </p>
                </div>
                <Button onClick={() => navigate('/documents')} data-testid="upload-document-btn">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                </Button>
            </div>

            {/* Stats Grid */}
            <motion.div 
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                variants={container}
                initial="hidden"
                animate="show"
            >
                <motion.div variants={item}>
                    <Card className="stat-card" data-testid="stat-total-documents">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                Total Documents
                            </CardTitle>
                            <FileText className="h-5 w-5 text-primary" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold font-mono">{stats?.total_documents || 0}</div>
                            <p className="text-xs text-muted-foreground mt-1">
                                All uploaded invoices
                            </p>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card" data-testid="stat-pending-documents">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                Pending Review
                            </CardTitle>
                            <Clock className="h-5 w-5 text-warning" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold font-mono text-warning">
                                {stats?.pending_documents || 0}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Awaiting approval
                            </p>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card" data-testid="stat-processed-documents">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                Processed
                            </CardTitle>
                            <CheckCircle className="h-5 w-5 text-success" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold font-mono text-success">
                                {stats?.processed_documents || 0}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Approved invoices
                            </p>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card" data-testid="stat-time-saved">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                Time Saved
                            </CardTitle>
                            <TrendingUp className="h-5 w-5 text-info" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold font-mono text-info">
                                {stats?.time_saved_hours || 0}h
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Hours of manual work
                            </p>
                        </CardContent>
                    </Card>
                </motion.div>
            </motion.div>

            {/* Secondary Stats */}
            <motion.div 
                className="grid grid-cols-1 lg:grid-cols-2 gap-6"
                variants={container}
                initial="hidden"
                animate="show"
            >
                <motion.div variants={item}>
                    <Card data-testid="reconciliation-card">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <ArrowLeftRight className="h-5 w-5" />
                                Reconciliation Status
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Unmatched Transactions</span>
                                <span className="font-mono font-semibold">{stats?.unmatched_transactions || 0}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Total Transactions</span>
                                <span className="font-mono font-semibold">{stats?.total_transactions || 0}</span>
                            </div>
                            <Progress 
                                value={stats?.total_transactions > 0 
                                    ? ((stats?.total_transactions - stats?.unmatched_transactions) / stats?.total_transactions) * 100 
                                    : 100
                                } 
                                className="h-2"
                            />
                            <Button 
                                variant="outline" 
                                className="w-full" 
                                onClick={() => navigate('/reconciliation')}
                                data-testid="view-reconciliation-btn"
                            >
                                View Reconciliation
                            </Button>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card data-testid="vat-risk-card">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5" />
                                VAT Risk Score
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Current Risk Level</span>
                                <span className={`font-semibold ${riskInfo.color}`}>{riskInfo.label}</span>
                            </div>
                            <div className="relative pt-4">
                                <div className="flex justify-between text-xs text-muted-foreground mb-2">
                                    <span>Low</span>
                                    <span>Medium</span>
                                    <span>High</span>
                                </div>
                                <Progress 
                                    value={stats?.vat_risk_score || 0} 
                                    className={`h-3 ${riskInfo.level === 'high' ? '[&>div]:bg-destructive' : riskInfo.level === 'medium' ? '[&>div]:bg-warning' : '[&>div]:bg-success'}`}
                                />
                            </div>
                            <Button 
                                variant="outline" 
                                className="w-full" 
                                onClick={() => navigate('/vat')}
                                data-testid="view-vat-btn"
                            >
                                View VAT Analysis
                            </Button>
                        </CardContent>
                    </Card>
                </motion.div>
            </motion.div>

            {/* Quick Actions */}
            {!currentTenant && (
                <motion.div variants={item} initial="hidden" animate="show">
                    <Card className="border-dashed border-2" data-testid="no-company-card">
                        <CardContent className="flex flex-col items-center justify-center py-12">
                            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                                <FileText className="h-8 w-8 text-primary" />
                            </div>
                            <h3 className="font-heading text-xl font-semibold mb-2">Get Started</h3>
                            <p className="text-muted-foreground text-center mb-6 max-w-md">
                                Create your first company to start uploading and processing invoices with AI
                            </p>
                            <Button onClick={() => navigate('/companies')} data-testid="create-company-btn">
                                Create Company
                            </Button>
                        </CardContent>
                    </Card>
                </motion.div>
            )}
        </div>
    );
}
