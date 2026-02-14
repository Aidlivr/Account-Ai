import React, { useState, useEffect } from 'react';
import { ArrowLeftRight, Check, X, AlertTriangle, Search, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { reconciliationAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Checkbox } from '../../components/ui/checkbox';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../../components/ui/table';
import { toast } from 'sonner';
import { formatCurrency, formatDate, calculateConfidenceColor } from '../../lib/utils';

export default function ReconciliationPage() {
    const { currentTenant } = useTenant();
    const navigate = useNavigate();
    const [data, setData] = useState({ transactions: [], suggestions: [] });
    const [loading, setLoading] = useState(true);
    const [selectedMatches, setSelectedMatches] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');

    const fetchData = async () => {
        if (!currentTenant) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            const response = await reconciliationAPI.getUnmatched(currentTenant.id);
            setData(response.data);
        } catch (err) {
            console.error('Failed to fetch reconciliation data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [currentTenant]);

    const handleMatch = async (suggestion) => {
        try {
            await reconciliationAPI.match(currentTenant.id, {
                transaction_id: suggestion.transaction_id,
                invoice_id: suggestion.invoice_id,
                confidence: suggestion.confidence,
            });
            toast.success('Transaction matched successfully');
            fetchData();
        } catch (err) {
            toast.error('Failed to match transaction');
        }
    };

    const handleBulkApprove = async () => {
        if (selectedMatches.length === 0) {
            toast.error('No matches selected');
            return;
        }

        try {
            await reconciliationAPI.bulkApprove(currentTenant.id, selectedMatches);
            toast.success(`${selectedMatches.length} transactions matched`);
            setSelectedMatches([]);
            fetchData();
        } catch (err) {
            toast.error('Bulk approval failed');
        }
    };

    const toggleMatch = (suggestion) => {
        const match = {
            transaction_id: suggestion.transaction_id,
            invoice_id: suggestion.invoice_id,
            confidence: suggestion.confidence,
        };

        setSelectedMatches(prev => {
            const exists = prev.find(m => m.transaction_id === match.transaction_id);
            if (exists) {
                return prev.filter(m => m.transaction_id !== match.transaction_id);
            }
            return [...prev, match];
        });
    };

    const filteredSuggestions = data.suggestions.filter(s => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            s.transaction_description?.toLowerCase().includes(query) ||
            s.invoice_supplier?.toLowerCase().includes(query)
        );
    });

    if (!currentTenant) {
        return (
            <div className="space-y-8" data-testid="reconciliation-page">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Reconciliation</h1>
                    <p className="text-muted-foreground mt-1">Match bank transactions with invoices</p>
                </div>
                <Card className="border-dashed border-2">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <AlertTriangle className="h-12 w-12 text-warning mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No Company Selected</h3>
                        <p className="text-muted-foreground text-center mb-6">
                            Please select a company to view reconciliation
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
        <div className="space-y-8" data-testid="reconciliation-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Reconciliation</h1>
                    <p className="text-muted-foreground mt-1">
                        Match bank transactions with invoices for {currentTenant.name}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Button variant="outline" onClick={fetchData} data-testid="refresh-btn">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    {selectedMatches.length > 0 && (
                        <Button onClick={handleBulkApprove} data-testid="bulk-approve-btn">
                            <Check className="h-4 w-4 mr-2" />
                            Approve {selectedMatches.length} Matches
                        </Button>
                    )}
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                            <ArrowLeftRight className="h-5 w-5 text-warning" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{data.transactions.length}</p>
                            <p className="text-sm text-muted-foreground">Unmatched Transactions</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Check className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{data.suggestions.length}</p>
                            <p className="text-sm text-muted-foreground">AI Match Suggestions</p>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                            <Check className="h-5 w-5 text-success" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold font-mono">{selectedMatches.length}</p>
                            <p className="text-sm text-muted-foreground">Selected for Approval</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Search */}
            <div className="relative max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search matches..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    data-testid="search-matches"
                />
            </div>

            {/* Suggestions Table */}
            <Card>
                <CardHeader>
                    <CardTitle>AI Match Suggestions</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {loading ? (
                        <div className="flex items-center justify-center py-16">
                            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : filteredSuggestions.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <ArrowLeftRight className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground">No match suggestions available</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="data-table-header">
                                    <TableHead className="w-12">
                                        <Checkbox
                                            checked={selectedMatches.length === filteredSuggestions.length}
                                            onCheckedChange={(checked) => {
                                                if (checked) {
                                                    setSelectedMatches(filteredSuggestions.map(s => ({
                                                        transaction_id: s.transaction_id,
                                                        invoice_id: s.invoice_id,
                                                        confidence: s.confidence,
                                                    })));
                                                } else {
                                                    setSelectedMatches([]);
                                                }
                                            }}
                                            data-testid="select-all-checkbox"
                                        />
                                    </TableHead>
                                    <TableHead>Transaction</TableHead>
                                    <TableHead>Amount</TableHead>
                                    <TableHead>Invoice Supplier</TableHead>
                                    <TableHead>Invoice Amount</TableHead>
                                    <TableHead>Confidence</TableHead>
                                    <TableHead className="w-24">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredSuggestions.map((suggestion, idx) => {
                                    const isSelected = selectedMatches.some(m => m.transaction_id === suggestion.transaction_id);
                                    return (
                                        <TableRow key={idx} className="data-table-row">
                                            <TableCell className="data-table-cell">
                                                <Checkbox
                                                    checked={isSelected}
                                                    onCheckedChange={() => toggleMatch(suggestion)}
                                                    data-testid={`match-checkbox-${idx}`}
                                                />
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <span className="truncate max-w-[200px] block">
                                                    {suggestion.transaction_description || 'No description'}
                                                </span>
                                            </TableCell>
                                            <TableCell className="data-table-cell font-mono">
                                                {formatCurrency(suggestion.transaction_amount)}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                {suggestion.invoice_supplier || '-'}
                                            </TableCell>
                                            <TableCell className="data-table-cell font-mono">
                                                {formatCurrency(suggestion.invoice_amount)}
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Badge className={calculateConfidenceColor(suggestion.confidence)}>
                                                    {Math.round(suggestion.confidence * 100)}%
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="data-table-cell">
                                                <Button
                                                    size="sm"
                                                    onClick={() => handleMatch(suggestion)}
                                                    data-testid={`match-btn-${idx}`}
                                                >
                                                    <Check className="h-4 w-4" />
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
