import React, { useState, useEffect, useCallback } from 'react';
import { FileText, Upload, Eye, CheckCircle, XCircle, Clock, AlertTriangle, Search, Edit2, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { documentAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
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
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../../components/ui/tooltip';
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

// Field display names
const FIELD_LABELS = {
    supplier_name: 'Supplier',
    cvr_number: 'CVR Number',
    invoice_number: 'Invoice #',
    invoice_date: 'Invoice Date',
    due_date: 'Due Date',
    net_amount: 'Net Amount',
    vat_amount: 'VAT Amount',
    total_amount: 'Total',
    vat_percentage: 'VAT %',
    currency: 'Currency',
    account_code: 'Account Code',
    account_name: 'Account Name',
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
    const [isEditing, setIsEditing] = useState(false);
    const [editedFields, setEditedFields] = useState({});
    const [approving, setApproving] = useState(false);

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
            toast.success('Document uploaded! AI is extracting data...');
            fetchDocuments();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
            event.target.value = '';
        }
    };

    const openDocumentDetail = async (doc) => {
        try {
            const response = await documentAPI.getOne(doc.id);
            setSelectedDoc(response.data);
            setEditedFields({});
            setIsEditing(false);
            setIsDetailOpen(true);
        } catch (err) {
            toast.error('Failed to load document details');
        }
    };

    const handleFieldEdit = (field, value) => {
        setEditedFields(prev => ({ ...prev, [field]: value }));
    };

    const handleSaveEdits = async () => {
        if (Object.keys(editedFields).length === 0) {
            setIsEditing(false);
            return;
        }

        try {
            await documentAPI.editFields(selectedDoc.id, editedFields);
            toast.success('Fields updated');
            
            // Refresh document
            const response = await documentAPI.getOne(selectedDoc.id);
            setSelectedDoc(response.data);
            setEditedFields({});
            setIsEditing(false);
        } catch (err) {
            toast.error('Failed to save changes');
        }
    };

    const handleApprove = async (approved) => {
        setApproving(true);
        try {
            // Merge edited fields with extracted data for final submission
            const finalData = {
                ...selectedDoc.extracted_data,
                ...editedFields
            };
            
            const accountMapping = {
                account_code: selectedDoc.ai_suggestions?.account_code || '4000',
                account_name: selectedDoc.ai_suggestions?.account_name || 'Varekøb',
                vat_code: selectedDoc.ai_suggestions?.vat_code || '25'
            };
            
            const result = await documentAPI.approve(selectedDoc.id, approved, finalData, accountMapping);
            
            if (approved && result.data.voucher_id) {
                toast.success(
                    <div>
                        <p className="font-semibold">Invoice approved!</p>
                        <p className="text-sm">Draft voucher created and ready to push.</p>
                    </div>
                );
            } else if (!approved) {
                toast.info('Document rejected');
            }
            
            fetchDocuments();
            setIsDetailOpen(false);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Action failed');
        } finally {
            setApproving(false);
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

    const getConfidenceIndicator = (confidence) => {
        if (confidence >= 0.8) return { color: 'bg-success', label: 'High' };
        if (confidence >= 0.5) return { color: 'bg-warning', label: 'Medium' };
        return { color: 'bg-destructive', label: 'Low' };
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
                                    <TableHead>AI Confidence</TableHead>
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
                                        const confidenceInfo = getConfidenceIndicator(doc.overall_confidence || 0);
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
                                                    {doc.overall_confidence !== null && doc.overall_confidence !== undefined && (
                                                        <TooltipProvider>
                                                            <Tooltip>
                                                                <TooltipTrigger asChild>
                                                                    <div className="flex items-center gap-2">
                                                                        <div className={`w-2 h-2 rounded-full ${confidenceInfo.color}`} />
                                                                        <span className="font-mono">
                                                                            {Math.round(doc.overall_confidence * 100)}%
                                                                        </span>
                                                                        {doc.uncertain_fields?.length > 0 && (
                                                                            <AlertTriangle className="h-3 w-3 text-warning" />
                                                                        )}
                                                                    </div>
                                                                </TooltipTrigger>
                                                                <TooltipContent>
                                                                    {doc.uncertain_fields?.length > 0 
                                                                        ? `${doc.uncertain_fields.length} fields need review`
                                                                        : 'All fields confident'
                                                                    }
                                                                </TooltipContent>
                                                            </Tooltip>
                                                        </TooltipProvider>
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
                <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <FileText className="h-5 w-5" />
                            Document Review
                        </DialogTitle>
                        <DialogDescription>
                            {selectedDoc?.filename}
                        </DialogDescription>
                    </DialogHeader>
                    
                    {selectedDoc && (
                        <div className="space-y-6 py-4">
                            {/* Overall Confidence */}
                            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <Sparkles className="h-5 w-5 text-primary" />
                                    <div>
                                        <p className="font-semibold">AI Extraction Confidence</p>
                                        <p className="text-sm text-muted-foreground">
                                            {selectedDoc.uncertain_fields?.length > 0 
                                                ? `${selectedDoc.uncertain_fields.length} fields need your attention`
                                                : 'All fields extracted with high confidence'
                                            }
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className={`text-2xl font-bold font-mono ${calculateConfidenceColor(selectedDoc.overall_confidence || 0)}`}>
                                        {Math.round((selectedDoc.overall_confidence || 0) * 100)}%
                                    </p>
                                    <Badge variant={getStatusBadge(selectedDoc.status).variant}>
                                        {getStatusBadge(selectedDoc.status).label}
                                    </Badge>
                                </div>
                            </div>

                            {/* Extracted Data with Confidence */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                                        Extracted Invoice Data
                                    </h4>
                                    {selectedDoc.status === 'review' && (
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => {
                                                if (isEditing) {
                                                    handleSaveEdits();
                                                } else {
                                                    setIsEditing(true);
                                                }
                                            }}
                                            data-testid="edit-toggle-btn"
                                        >
                                            <Edit2 className="h-4 w-4 mr-2" />
                                            {isEditing ? 'Save Changes' : 'Edit Fields'}
                                        </Button>
                                    )}
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4">
                                    {Object.entries(FIELD_LABELS).map(([field, label]) => {
                                        const fieldData = selectedDoc.field_confidence?.[field];
                                        const value = editedFields[field] ?? selectedDoc.extracted_data?.[field];
                                        const confidence = fieldData?.confidence;
                                        const isUncertain = fieldData?.uncertain;
                                        const source = fieldData?.source;
                                        
                                        // Skip line_items and empty fields
                                        if (field === 'line_items') return null;
                                        
                                        return (
                                            <div key={field} className={`p-3 rounded-md ${isUncertain ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
                                                <div className="flex items-center justify-between mb-1">
                                                    <Label className="text-sm text-muted-foreground">{label}</Label>
                                                    {confidence !== undefined && (
                                                        <div className="flex items-center gap-1">
                                                            {source === 'user_edited' && (
                                                                <Badge variant="outline" className="text-xs">Edited</Badge>
                                                            )}
                                                            {source === 'vendor_learned' && (
                                                                <Badge variant="secondary" className="text-xs">Learned</Badge>
                                                            )}
                                                            <span className={`text-xs font-mono ${calculateConfidenceColor(confidence)}`}>
                                                                {Math.round(confidence * 100)}%
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                                {isEditing && selectedDoc.status === 'review' ? (
                                                    <Input
                                                        value={value ?? ''}
                                                        onChange={(e) => handleFieldEdit(field, e.target.value)}
                                                        className={isUncertain ? 'border-warning' : ''}
                                                        data-testid={`edit-field-${field}`}
                                                    />
                                                ) : (
                                                    <p className={`font-medium ${field.includes('amount') ? 'font-mono' : ''}`}>
                                                        {field.includes('amount') && value 
                                                            ? formatCurrency(value) 
                                                            : value || '-'
                                                        }
                                                    </p>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* AI Suggestions & Validations */}
                            {selectedDoc.ai_suggestions && (
                                <div className="space-y-4">
                                    <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                                        AI Validations & Suggestions
                                    </h4>
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                                            <span>CVR Valid (8 digits)</span>
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
                                                <Badge variant="warning"><AlertTriangle className="h-3 w-3 mr-1" /> Check VAT</Badge>
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
                                        {selectedDoc.ai_suggestions.vendor_pattern_found && (
                                            <div className="flex items-center justify-between p-3 bg-primary/10 rounded-md border border-primary/30">
                                                <span className="flex items-center gap-2">
                                                    <Sparkles className="h-4 w-4 text-primary" />
                                                    Vendor Pattern Found
                                                </span>
                                                <Badge variant="secondary">
                                                    Used {selectedDoc.ai_suggestions.vendor_usage_count || 0}x before
                                                </Badge>
                                            </div>
                                        )}
                                        {selectedDoc.ai_suggestions.account_code && (
                                            <div className="p-3 bg-muted/50 rounded-md">
                                                <div className="flex items-center justify-between">
                                                    <span>Suggested Account</span>
                                                    <span className={`font-mono ${calculateConfidenceColor(selectedDoc.ai_suggestions.account_confidence || 0)}`}>
                                                        {Math.round((selectedDoc.ai_suggestions.account_confidence || 0) * 100)}% confident
                                                    </span>
                                                </div>
                                                <p className="font-mono mt-1">
                                                    {selectedDoc.ai_suggestions.account_code} - {selectedDoc.ai_suggestions.account_name}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Actions */}
                            {selectedDoc.status === 'review' && (
                                <DialogFooter className="gap-3 pt-4">
                                    <Button 
                                        variant="outline" 
                                        className="border-destructive text-destructive hover:bg-destructive/10"
                                        onClick={() => handleApprove(false)}
                                        disabled={approving}
                                        data-testid="reject-doc-btn"
                                    >
                                        <XCircle className="h-4 w-4 mr-2" />
                                        Reject
                                    </Button>
                                    <Button 
                                        onClick={() => handleApprove(true)}
                                        disabled={approving}
                                        data-testid="approve-doc-btn"
                                    >
                                        {approving ? (
                                            <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                                        ) : (
                                            <CheckCircle className="h-4 w-4 mr-2" />
                                        )}
                                        Approve & Create Voucher
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
