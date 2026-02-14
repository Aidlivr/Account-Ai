import React, { useState, useEffect } from 'react';
import { UsersRound, Building2, FileText, AlertTriangle, Clock, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { dashboardAPI } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
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
import { toast } from 'sonner';
import { getRiskLevel } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function AccountantDashboard() {
    const navigate = useNavigate();
    const [overview, setOverview] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await dashboardAPI.getAccountantOverview();
                setOverview(response.data);
            } catch (err) {
                console.error('Failed to fetch accountant overview:', err);
                toast.error('Failed to load client overview');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center py-16">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    const totalPending = overview?.clients?.reduce((sum, c) => sum + c.pending_documents, 0) || 0;
    const totalAnomalies = overview?.clients?.reduce((sum, c) => sum + c.anomalies_count, 0) || 0;

    return (
        <div className="space-y-8" data-testid="accountant-dashboard">
            {/* Header */}
            <div>
                <h1 className="font-heading text-3xl font-bold">Client Overview</h1>
                <p className="text-muted-foreground mt-1">
                    Multi-client dashboard for accountants
                </p>
            </div>

            {/* Summary Stats */}
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
                                <Building2 className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono">{overview?.total_clients || 0}</p>
                                <p className="text-sm text-muted-foreground">Total Clients</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
                
                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                                <Clock className="h-5 w-5 text-warning" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono text-warning">{totalPending}</p>
                                <p className="text-sm text-muted-foreground">Pending Documents</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center">
                                <AlertTriangle className="h-5 w-5 text-destructive" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono text-destructive">{totalAnomalies}</p>
                                <p className="text-sm text-muted-foreground">Risk Alerts</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div variants={item}>
                    <Card className="stat-card">
                        <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                                <TrendingUp className="h-5 w-5 text-success" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold font-mono text-success">
                                    {Math.round((overview?.total_clients || 0) * 2.5)}h
                                </p>
                                <p className="text-sm text-muted-foreground">Time Saved</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            </motion.div>

            {/* Clients Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <UsersRound className="h-5 w-5" />
                        All Clients
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {!overview?.clients?.length ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <Building2 className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground">No clients assigned yet</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="data-table-header">
                                    <TableHead>Client</TableHead>
                                    <TableHead>Pending Docs</TableHead>
                                    <TableHead>Risk Score</TableHead>
                                    <TableHead>Anomalies</TableHead>
                                    <TableHead className="w-32">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {overview.clients.map((client) => {
                                    const riskInfo = getRiskLevel(client.risk_score);
                                    return (
                                        <TableRow key={client.tenant_id} className="data-table-row">
                                            <TableCell className="data-table-cell">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                                                        <Building2 className="h-4 w-4 text-primary" />
                                                    </div>
                                                    <span className="font-medium">{client.tenant_name}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                {client.pending_documents > 0 ? (
                                                    <Badge variant="warning">
                                                        {client.pending_documents} pending
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="secondary">None</Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <div className="flex items-center gap-2">
                                                    <Progress 
                                                        value={client.risk_score} 
                                                        className={`w-16 h-2 ${
                                                            riskInfo.level === 'high' ? '[&>div]:bg-destructive' : 
                                                            riskInfo.level === 'medium' ? '[&>div]:bg-warning' : '[&>div]:bg-success'
                                                        }`}
                                                    />
                                                    <span className={`font-mono text-sm ${riskInfo.color}`}>
                                                        {client.risk_score}
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                {client.anomalies_count > 0 ? (
                                                    <Badge variant="destructive">
                                                        {client.anomalies_count} issues
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="success">Clear</Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Button 
                                                    size="sm" 
                                                    variant="outline"
                                                    onClick={() => {
                                                        // Select tenant and navigate
                                                        localStorage.setItem('currentTenantId', client.tenant_id);
                                                        navigate('/documents');
                                                    }}
                                                    data-testid={`view-client-${client.tenant_id}`}
                                                >
                                                    View
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
