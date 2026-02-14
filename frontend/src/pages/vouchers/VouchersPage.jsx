import React, { useState, useEffect } from 'react';
import { Receipt, Upload, CheckCircle, Clock, AlertTriangle, Eye, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { voucherAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
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
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '../../components/ui/dialog';
import { toast } from 'sonner';
import { formatCurrency, formatDate } from '../../lib/utils';
import { ExportButton } from '../../components/export/ExportButton';

export default function VouchersPage() {
    const { currentTenant } = useTenant();
    const navigate = useNavigate();
    const [vouchers, setVouchers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedVoucher, setSelectedVoucher] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const [pushing, setPushing] = useState(false);

    useEffect(() => {
        if (currentTenant) {
            fetchVouchers();
        } else {
            setLoading(false);
        }
    }, [currentTenant]);

    const fetchVouchers = async () => {
        try {
            const response = await voucherAPI.getAll(currentTenant.id);
            setVouchers(response.data);
        } catch (err) {
            console.error('Failed to fetch vouchers:', err);
        } finally {
            setLoading(false);
        }
    };

    const openVoucherDetail = async (voucher) => {
        try {
            const response = await voucherAPI.getOne(currentTenant.id, voucher.id);
            setSelectedVoucher(response.data);
            setIsDetailOpen(true);
        } catch (err) {
            toast.error('Failed to load voucher details');
        }
    };

    const handlePushVoucher = async () => {
        setPushing(true);
        try {
            const result = await voucherAPI.push(currentTenant.id, selectedVoucher.id);
            
            if (result.data.success) {
                toast.success('Voucher pushed to accounting system');
                fetchVouchers();
                setIsDetailOpen(false);
            } else {
                toast.info(result.data.error || 'Awaiting accounting system integration');
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Push failed');
        } finally {
            setPushing(false);
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'draft':
                return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" /> Draft</Badge>;
            case 'ready_to_push':
                return <Badge variant="warning"><ArrowRight className="h-3 w-3 mr-1" /> Ready to Push</Badge>;
            case 'pushed':
                return <Badge variant="success"><CheckCircle className="h-3 w-3 mr-1" /> Pushed</Badge>;
            case 'failed':
                return <Badge variant="destructive"><AlertTriangle className="h-3 w-3 mr-1" /> Failed</Badge>;
            default:
                return <Badge variant="outline">{status}</Badge>;
        }
    };

    if (!currentTenant) {
        return (
            <div className="space-y-8" data-testid="vouchers-page">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Vouchers</h1>
                    <p className="text-muted-foreground mt-1">Draft vouchers ready for accounting system</p>
                </div>
                <Card className="border-dashed border-2">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <AlertTriangle className="h-12 w-12 text-warning mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No Company Selected</h3>
                        <Button onClick={() => navigate('/companies')}>Go to Companies</Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const readyCount = vouchers.filter(v => v.status === 'ready_to_push').length;

    return (
        <div className="space-y-8" data-testid="vouchers-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Vouchers</h1>
                    <p className="text-muted-foreground mt-1">
                        Draft vouchers for {currentTenant.name}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <ExportButton tenantId={currentTenant.id} type="vouchers" />
                    <Button onClick={() => navigate('/documents')} data-testid="go-to-documents">
                        <Upload className="h-4 w-4 mr-2" />
                        Process More Invoices
                    </Button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Receipt className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{vouchers.length}</p>
                            <p className="text-sm text-muted-foreground">Total Vouchers</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                            <ArrowRight className="h-5 w-5 text-warning" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono text-warning">{readyCount}</p>
                            <p className="text-sm text-muted-foreground">Ready to Push</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                            <CheckCircle className="h-5 w-5 text-success" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono text-success">
                                {vouchers.filter(v => v.status === 'pushed').length}
                            </p>
                            <p className="text-sm text-muted-foreground">Pushed</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Vouchers Table */}
            <Card>
                <CardHeader>
                    <CardTitle>All Vouchers</CardTitle>
                    <CardDescription>
                        Approved invoices converted to accounting vouchers
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                    {loading ? (
                        <div className="flex items-center justify-center py-16">
                            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : vouchers.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <Receipt className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground mb-4">No vouchers yet</p>
                            <Button variant="outline" onClick={() => navigate('/documents')}>
                                Process Invoices First
                            </Button>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="data-table-header">
                                    <TableHead>Supplier</TableHead>
                                    <TableHead>Invoice #</TableHead>
                                    <TableHead>Amount</TableHead>
                                    <TableHead>Account</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead className="w-24">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {vouchers.map((voucher) => (
                                    <TableRow key={voucher.id} className="data-table-row">
                                        <TableCell className="data-table-cell font-medium">
                                            {voucher.voucher_data?.supplier_name || '-'}
                                        </TableCell>
                                        <TableCell className="data-table-cell font-mono">
                                            {voucher.voucher_data?.invoice_number || '-'}
                                        </TableCell>
                                        <TableCell className="data-table-cell font-mono">
                                            {formatCurrency(voucher.voucher_data?.total_amount)}
                                        </TableCell>
                                        <TableCell className="data-table-cell font-mono">
                                            {voucher.account_mapping?.account_code} - {voucher.account_mapping?.account_name}
                                        </TableCell>
                                        <TableCell className="data-table-cell">
                                            {getStatusBadge(voucher.status)}
                                        </TableCell>
                                        <TableCell className="data-table-cell text-muted-foreground">
                                            {formatDate(voucher.created_at)}
                                        </TableCell>
                                        <TableCell className="data-table-cell">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => openVoucherDetail(voucher)}
                                                data-testid={`view-voucher-${voucher.id}`}
                                            >
                                                <Eye className="h-4 w-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Voucher Detail Dialog */}
            <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Receipt className="h-5 w-5" />
                            Voucher Preview
                        </DialogTitle>
                        <DialogDescription>
                            Review voucher before pushing to accounting system
                        </DialogDescription>
                    </DialogHeader>
                    
                    {selectedVoucher && (
                        <div className="space-y-6 py-4">
                            {/* Header Info */}
                            <div className="grid grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
                                <div>
                                    <p className="text-sm text-muted-foreground">Supplier</p>
                                    <p className="font-semibold">{selectedVoucher.voucher_data?.supplier_name}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Invoice Number</p>
                                    <p className="font-mono">{selectedVoucher.voucher_data?.invoice_number}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Invoice Date</p>
                                    <p>{selectedVoucher.voucher_data?.invoice_date || '-'}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Due Date</p>
                                    <p>{selectedVoucher.voucher_data?.due_date || '-'}</p>
                                </div>
                            </div>

                            {/* Voucher Preview */}
                            <div className="space-y-4">
                                <h4 className="font-semibold">Accounting Entries</h4>
                                
                                {/* Debit Entries */}
                                <div className="border rounded-lg overflow-hidden">
                                    <div className="bg-muted/50 px-4 py-2 font-medium text-sm">Debit</div>
                                    {selectedVoucher.preview?.debit_entries?.map((entry, idx) => (
                                        <div key={idx} className="flex items-center justify-between px-4 py-3 border-t">
                                            <div>
                                                <p className="font-mono">{entry.account_code}</p>
                                                <p className="text-sm text-muted-foreground">{entry.account_name}</p>
                                            </div>
                                            <p className="font-mono font-semibold">{formatCurrency(entry.amount)}</p>
                                        </div>
                                    ))}
                                    {selectedVoucher.preview?.vat_entry && (
                                        <div className="flex items-center justify-between px-4 py-3 border-t bg-blue-50/50">
                                            <div>
                                                <p className="font-mono">{selectedVoucher.preview.vat_entry.account_code}</p>
                                                <p className="text-sm text-muted-foreground">{selectedVoucher.preview.vat_entry.account_name}</p>
                                            </div>
                                            <p className="font-mono font-semibold">{formatCurrency(selectedVoucher.preview.vat_entry.amount)}</p>
                                        </div>
                                    )}
                                </div>

                                {/* Credit Entries */}
                                <div className="border rounded-lg overflow-hidden">
                                    <div className="bg-muted/50 px-4 py-2 font-medium text-sm">Credit</div>
                                    {selectedVoucher.preview?.credit_entries?.map((entry, idx) => (
                                        <div key={idx} className="flex items-center justify-between px-4 py-3 border-t">
                                            <div>
                                                <p className="font-mono">{entry.account_code}</p>
                                                <p className="text-sm text-muted-foreground">{entry.account_name}</p>
                                            </div>
                                            <p className="font-mono font-semibold">{formatCurrency(entry.amount)}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Balance Check */}
                                <div className={`p-4 rounded-lg ${selectedVoucher.preview?.balanced ? 'bg-success/10 border border-success/30' : 'bg-destructive/10 border border-destructive/30'}`}>
                                    <div className="flex items-center justify-between">
                                        <span className="font-medium">Balance Status</span>
                                        {selectedVoucher.preview?.balanced ? (
                                            <Badge variant="success">
                                                <CheckCircle className="h-3 w-3 mr-1" /> Balanced
                                            </Badge>
                                        ) : (
                                            <Badge variant="destructive">
                                                <AlertTriangle className="h-3 w-3 mr-1" /> Unbalanced
                                            </Badge>
                                        )}
                                    </div>
                                    <div className="flex justify-between mt-2 text-sm">
                                        <span>Total Debit: <span className="font-mono">{formatCurrency(selectedVoucher.preview?.total_debit)}</span></span>
                                        <span>Total Credit: <span className="font-mono">{formatCurrency(selectedVoucher.preview?.total_credit)}</span></span>
                                    </div>
                                </div>
                            </div>

                            {/* Status */}
                            <div className="flex items-center justify-between p-4 border rounded-lg">
                                <div>
                                    <p className="font-medium">Voucher Status</p>
                                    <p className="text-sm text-muted-foreground">
                                        {selectedVoucher.status === 'ready_to_push' 
                                            ? 'Ready to push to accounting system'
                                            : selectedVoucher.status === 'pushed'
                                            ? 'Successfully pushed'
                                            : 'Draft voucher'
                                        }
                                    </p>
                                </div>
                                {getStatusBadge(selectedVoucher.status)}
                            </div>

                            {/* Push Action */}
                            {selectedVoucher.status === 'ready_to_push' && (
                                <DialogFooter>
                                    <Button
                                        onClick={handlePushVoucher}
                                        disabled={pushing}
                                        className="w-full"
                                        data-testid="push-voucher-btn"
                                    >
                                        {pushing ? (
                                            <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                                        ) : (
                                            <ArrowRight className="h-4 w-4 mr-2" />
                                        )}
                                        Push to Accounting System
                                    </Button>
                                </DialogFooter>
                            )}
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
