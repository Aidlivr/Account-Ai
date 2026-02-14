import React, { useState, useEffect, useCallback } from 'react';
import { FileText, Upload, Eye, CheckCircle, XCircle, Clock, AlertTriangle, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { documentAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
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
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '../../components/ui/dialog';
import { toast } from 'sonner';
import { formatDate, formatCurrency, getStatusBadge, calculateConfidenceColor } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } }
};

const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 }
};

export default function DocumentsPage() {
    const { currentTenant, tenants } = useTenant();
    const navigate = useNavigate();
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [statusFilter, setStatusFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDoc, setSelectedDoc] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);

    const fetchDocuments = useCallback(async () => {
        if (!currentTenant) {
            setDocuments([]);
            setLoading(false);
            return;
        }

        try {
            const status = statusFilter === 'all' ? null : statusFilter;
            const response = await documentAPI.getAll(currentTenant.id, status);
            setDocuments(response.data);
        } catch (err) {
            console.error('Failed to fetch documents:', err);
            toast.error('Failed to load documents');
        } finally {
            setLoading(false);
        }
    }, [currentTenant, statusFilter]);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const handleFileUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (!currentTenant) {
            toast.error('Please select a company first');
            return;
        }

        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            toast.error('Invalid file type. Please upload JPG, PNG, or PDF');
            return;
        }

        setUploading(true);
        try {
            await documentAPI.upload(file, currentTenant.id);
            toast.success('Document uploaded! Processing with AI...');
            fetchDocuments();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
            event.target.value = '';
        }
    };

    const handleApprove = async (docId, approved) => {
        try {
            await documentAPI.approve(docId, approved);
            toast.success(approved ? 'Document approved' : 'Document rejected');
            fetchDocuments();
            setIsDetailOpen(false);
        } catch (err) {
            toast.error('Action failed');
        }
    };

    const openDocumentDetail = async (doc) => {
        try {
            const response = await documentAPI.getOne(doc.id);
            setSelectedDoc(response.data);
            setIsDetailOpen(true);
        } catch (err) {
            toast.error('Failed to load document details');
        }
    };

    const filteredDocs = documents.filter(doc => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            doc.filename?.toLowerCase().includes(query) ||
            doc.extracted_data?.supplier_name?.toLowerCase().includes(query) ||
            doc.extracted_data?.invoice_number?.toLowerCase().includes(query)
        );
    });

    const getStatusIcon = (status) => {
        switch (status) {
            case 'approved': return <CheckCircle className="h-4 w-4 text-success" />;
            case 'rejected': return <XCircle className="h-4 w-4 text-destructive" />;
            case 'review': return <Clock className="h-4 w-4 text-warning" />;
            case 'error': return <AlertTriangle className="h-4 w-4 text-destructive" />;
            default: return <Clock className="h-4 w-4 text-muted-foreground" />;
        }
    };

    if (!currentTenant) {
        return (
            <div className="space-y-8" data-testid="documents-page">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Documents</h1>
                    <p className="text-muted-foreground mt-1">Upload and process invoices with AI</p>
                </div>
                <Card className="border-dashed border-2">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <AlertTriangle className="h-12 w-12 text-warning mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No Company Selected</h3>
                        <p className="text-muted-foreground text-center mb-6">
                            Please select or create a company to manage documents
                        </p>
                        <Button onClick={() => navigate('/companies')}>
                            Go to Companies
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-8" data-testid="documents-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Documents</h1>
                    <p className="text-muted-foreground mt-1">
                        Upload and process invoices for {currentTenant.name}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        accept=".jpg,.jpeg,.png,.pdf"
                        onChange={handleFileUpload}
                        data-testid="file-upload-input"
                    />
                    <Button 
                        onClick={() => document.getElementById('file-upload')?.click()}
                        disabled={uploading}
                        data-testid="upload-btn"
                    >
                        {uploading ? (
                            <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                        ) : (
                            <Upload className="h-4 w-4 mr-2" />
                        )}
                        {uploading ? 'Uploading...' : 'Upload Document'}
                    </Button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search documents..."
                        className="pl-10"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        data-testid="search-documents"
                    />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-40" data-testid="status-filter">
                        <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="processing">Processing</SelectItem>
                        <SelectItem value="review">Pending Review</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {/* Documents Table */}
            <Card>
                <CardContent className="p-0">
                    {loading ? (
                        <div className="flex items-center justify-center py-16">
                            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : filteredDocs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground">No documents found</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="data-table-header">
                                    <TableHead>Document</TableHead>
                                    <TableHead>Supplier</TableHead>
                                    <TableHead>Invoice #</TableHead>
                                    <TableHead>Amount</TableHead>
                                    <TableHead>Confidence</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Date</TableHead>
                                    <TableHead className="w-24">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <motion.tbody
                                    variants={container}
                                    initial="hidden"
                                    animate="show"
                                    className="contents"
                                >
                                    {filteredDocs.map((doc) => {
                                        const statusInfo = getStatusBadge(doc.status);
                                        return (
                                            <motion.tr
                                                key={doc.id}
                                                variants={item}
                                                className="data-table-row"
                                            >
                                                <TableCell className="data-table-cell">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="h-4 w-4 text-muted-foreground" />
                                                        <span className="font-medium truncate max-w-[200px]">
                                                            {doc.filename}
                                                        </span>
                                                    </div>
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    {doc.extracted_data?.supplier_name || '-'}
                                                </TableCell>
                                                <TableCell className="data-table-cell font-mono">
                                                    {doc.extracted_data?.invoice_number || '-'}
                                                </TableCell>
                                                <TableCell className="data-table-cell font-mono">
                                                    {formatCurrency(doc.extracted_data?.total_amount, doc.extracted_data?.currency)}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    {doc.confidence_score !== null && (
                                                        <span className={`font-mono ${calculateConfidenceColor(doc.confidence_score)}`}>
                                                            {Math.round(doc.confidence_score * 100)}%
                                                        </span>
                                                    )}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    <Badge variant={statusInfo.variant}>
                                                        {getStatusIcon(doc.status)}
                                                        <span className="ml-1">{statusInfo.label}</span>
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="data-table-cell text-muted-foreground">
                                                    {formatDate(doc.created_at)}
                                                </TableCell>
                                                <TableCell className="data-table-cell">
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        onClick={() => openDocumentDetail(doc)}
                                                        data-testid={`view-doc-${doc.id}`}
                                                    >
                                                        <Eye className="h-4 w-4" />
                                                    </Button>
                                                </TableCell>
                                            </motion.tr>
                                        );
                                    })}
                                </motion.tbody>
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Document Detail Dialog */}
            <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <FileText className="h-5 w-5" />
                            Document Details
                        </DialogTitle>
                        <DialogDescription>
                            {selectedDoc?.filename}
                        </DialogDescription>
                    </DialogHeader>
                    
                    {selectedDoc && (
                        <div className="space-y-6 py-4">
                            {/* AI Extracted Data */}
                            <div className="space-y-4">
                                <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                                    AI Extracted Data
                                </h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground">Supplier</p>
                                        <p className="font-medium">{selectedDoc.extracted_data?.supplier_name || '-'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">CVR Number</p>
                                        <p className="font-mono">{selectedDoc.extracted_data?.cvr_number || '-'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Invoice Number</p>
                                        <p className="font-mono">{selectedDoc.extracted_data?.invoice_number || '-'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Invoice Date</p>
                                        <p>{selectedDoc.extracted_data?.invoice_date || '-'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Due Date</p>
                                        <p>{selectedDoc.extracted_data?.due_date || '-'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Net Amount</p>
                                        <p className="font-mono">{formatCurrency(selectedDoc.extracted_data?.net_amount)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">VAT Amount</p>
                                        <p className="font-mono">{formatCurrency(selectedDoc.extracted_data?.vat_amount)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Total Amount</p>
                                        <p className="font-mono font-bold text-lg">{formatCurrency(selectedDoc.extracted_data?.total_amount)}</p>
                                    </div>
                                </div>
                            </div>

                            {/* AI Suggestions */}
                            {selectedDoc.ai_suggestions && (
                                <div className="space-y-4">
                                    <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                                        AI Suggestions & Validations
                                    </h4>
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                                            <span>CVR Valid</span>
                                            {selectedDoc.ai_suggestions.cvr_valid ? (
                                                <Badge variant="success"><CheckCircle className="h-3 w-3 mr-1" /> Valid</Badge>
                                            ) : (
                                                <Badge variant="warning"><AlertTriangle className="h-3 w-3 mr-1" /> Invalid/Missing</Badge>
                                            )}
                                        </div>
                                        <div className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                                            <span>VAT Consistent (25%)</span>
                                            {selectedDoc.ai_suggestions.vat_consistent ? (
                                                <Badge variant="success"><CheckCircle className="h-3 w-3 mr-1" /> Consistent</Badge>
                                            ) : (
                                                <Badge variant="warning"><AlertTriangle className="h-3 w-3 mr-1" /> Inconsistent</Badge>
                                            )}
                                        </div>
                                        <div className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                                            <span>Duplicate Check</span>
                                            {selectedDoc.ai_suggestions.is_duplicate ? (
                                                <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" /> Potential Duplicate</Badge>
                                            ) : (
                                                <Badge variant="success"><CheckCircle className="h-3 w-3 mr-1" /> Unique</Badge>
                                            )}
                                        </div>
                                        {selectedDoc.ai_suggestions.account_code && (
                                            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                                                <span>Suggested Account</span>
                                                <span className="font-mono">
                                                    {selectedDoc.ai_suggestions.account_code} - {selectedDoc.ai_suggestions.account_name}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Confidence Score */}
                            <div className="flex items-center justify-between p-4 bg-card border rounded-lg">
                                <div>
                                    <p className="text-sm text-muted-foreground">AI Confidence Score</p>
                                    <p className={`text-2xl font-bold font-mono ${calculateConfidenceColor(selectedDoc.confidence_score || 0)}`}>
                                        {Math.round((selectedDoc.confidence_score || 0) * 100)}%
                                    </p>
                                </div>
                                <Badge variant={getStatusBadge(selectedDoc.status).variant}>
                                    {getStatusBadge(selectedDoc.status).label}
                                </Badge>
                            </div>

                            {/* Actions */}
                            {selectedDoc.status === 'review' && (
                                <div className="flex gap-3 pt-4">
                                    <Button 
                                        variant="outline" 
                                        className="flex-1 border-destructive text-destructive hover:bg-destructive/10"
                                        onClick={() => handleApprove(selectedDoc.id, false)}
                                        data-testid="reject-doc-btn"
                                    >
                                        <XCircle className="h-4 w-4 mr-2" />
                                        Reject
                                    </Button>
                                    <Button 
                                        className="flex-1"
                                        onClick={() => handleApprove(selectedDoc.id, true)}
                                        data-testid="approve-doc-btn"
                                    >
                                        <CheckCircle className="h-4 w-4 mr-2" />
                                        Approve
                                    </Button>
                                </div>
                            )}
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
