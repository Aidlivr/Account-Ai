import React, { useState, useEffect } from 'react';
import { Calculator, AlertTriangle, TrendingUp, FileText, Download, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { vatAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
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
import { formatCurrency, getRiskLevel } from '../../lib/utils';

export default function VATPage() {
    const { currentTenant } = useTenant();
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchAnalysis = async () => {
        if (!currentTenant) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            const response = await vatAPI.getAnalysis(currentTenant.id);
            setAnalysis(response.data);
        } catch (err) {
            console.error('Failed to fetch VAT analysis:', err);
            toast.error('Failed to load VAT analysis');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnalysis();
    }, [currentTenant]);

    const handleGenerateReport = async () => {
        if (!analysis) return;

        try {
            await vatAPI.generateReport(
                currentTenant.id,
                analysis.period_start,
                analysis.period_end
            );
            toast.success('VAT report generated');
        } catch (err) {
            toast.error('Failed to generate report');
        }
    };

    if (!currentTenant) {
        return (
            <div className="space-y-8" data-testid="vat-page">
                <div>
                    <h1 className="font-heading text-3xl font-bold">VAT Analysis</h1>
                    <p className="text-muted-foreground mt-1">Analyze VAT patterns and detect risks</p>
                </div>
                <Card className="border-dashed border-2">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <AlertTriangle className="h-12 w-12 text-warning mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No Company Selected</h3>
                        <p className="text-muted-foreground text-center mb-6">
                            Please select a company to view VAT analysis
                        </p>
                        <Button onClick={() => navigate('/companies')}>
                            Go to Companies
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const riskInfo = getRiskLevel(analysis?.risk_score || 0);

    return (
        <div className="space-y-8" data-testid="vat-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">VAT Analysis</h1>
                    <p className="text-muted-foreground mt-1">
                        Risk assessment for {currentTenant.name}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Button variant="outline" onClick={fetchAnalysis} data-testid="refresh-vat-btn">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    <Button onClick={handleGenerateReport} data-testid="generate-report-btn">
                        <Download className="h-4 w-4 mr-2" />
                        Generate Report
                    </Button>
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-16">
                    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                </div>
            ) : (
                <>
                    {/* Risk Score Card */}
                    <Card className="overflow-hidden" data-testid="risk-score-card">
                        <div className={`h-2 ${riskInfo.level === 'high' ? 'bg-destructive' : riskInfo.level === 'medium' ? 'bg-warning' : 'bg-success'}`} />
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground uppercase tracking-wider">VAT Risk Score</p>
                                    <div className="flex items-center gap-4 mt-2">
                                        <span className={`text-5xl font-bold font-mono ${riskInfo.color}`}>
                                            {analysis?.risk_score || 0}
                                        </span>
                                        <Badge variant={riskInfo.level === 'high' ? 'destructive' : riskInfo.level === 'medium' ? 'warning' : 'success'}>
                                            {riskInfo.label}
                                        </Badge>
                                    </div>
                                </div>
                                <div className="w-32">
                                    <Progress 
                                        value={analysis?.risk_score || 0} 
                                        className={`h-4 ${riskInfo.level === 'high' ? '[&>div]:bg-destructive' : riskInfo.level === 'medium' ? '[&>div]:bg-warning' : '[&>div]:bg-success'}`}
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Summary Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Total Purchases</p>
                                <p className="text-2xl font-bold font-mono mt-1">
                                    {formatCurrency(analysis?.summary?.total_purchases || 0)}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">VAT Paid</p>
                                <p className="text-2xl font-bold font-mono mt-1">
                                    {formatCurrency(analysis?.summary?.total_vat_paid || 0)}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Total Amount</p>
                                <p className="text-2xl font-bold font-mono mt-1">
                                    {formatCurrency(analysis?.summary?.total_amount || 0)}
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4">
                                <p className="text-sm text-muted-foreground">Documents Analyzed</p>
                                <p className="text-2xl font-bold font-mono mt-1">
                                    {analysis?.summary?.document_count || 0}
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Anomalies */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5" />
                                Detected Anomalies
                            </CardTitle>
                            <CardDescription>
                                Issues found during VAT analysis that require attention
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {analysis?.anomalies?.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-8">
                                    <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center mb-4">
                                        <TrendingUp className="h-6 w-6 text-success" />
                                    </div>
                                    <p className="text-muted-foreground">No anomalies detected</p>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow className="data-table-header">
                                            <TableHead>Type</TableHead>
                                            <TableHead>Severity</TableHead>
                                            <TableHead>Document</TableHead>
                                            <TableHead>Details</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {analysis?.anomalies?.map((anomaly, idx) => (
                                            <TableRow key={idx} className="data-table-row">
                                                <TableCell className="data-table-cell capitalize">
                                                    {anomaly.type.replace('_', ' ')}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    <Badge 
                                                        variant={anomaly.severity === 'high' ? 'destructive' : anomaly.severity === 'medium' ? 'warning' : 'secondary'}
                                                    >
                                                        {anomaly.severity}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    {anomaly.filename || '-'}
                                                </TableCell>
                                                <TableCell className="data-table-cell text-muted-foreground">
                                                    {anomaly.details}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>

                    {/* AI Risk Summary */}
                    {analysis?.ai_risk_summary && (
                        <Card data-testid="ai-summary-card">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Calculator className="h-5 w-5" />
                                    AI Risk Analysis
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="prose prose-sm max-w-none">
                                    <p className="text-muted-foreground whitespace-pre-wrap">
                                        {analysis.ai_risk_summary}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </>
            )}
        </div>
    );
}
