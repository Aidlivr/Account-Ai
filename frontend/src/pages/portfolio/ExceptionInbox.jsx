import React, { useState, useEffect } from 'react';
import { 
    Bell, 
    AlertTriangle, 
    ChevronRight,
    Filter,
    RefreshCw,
    CheckCircle,
    Search,
    Eye,
    UserPlus,
    X,
    TrendingUp,
    Copy,
    User,
    FileWarning,
    BarChart3
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Exception type icons
const ExceptionIcon = ({ type }) => {
    const icons = {
        expense_spike: TrendingUp,
        duplicate_invoice: Copy,
        unusual_vendor: User,
        vat_variance: FileWarning,
        pattern_deviation: BarChart3,
        vat_trend: TrendingUp,
    };
    const Icon = icons[type] || AlertTriangle;
    return <Icon className="w-4 h-4" />;
};

// Severity badge
const SeverityBadge = ({ severity }) => {
    const styles = {
        high: 'bg-red-500/10 text-red-400 border-red-500/20',
        medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        low: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
    };
    return (
        <span className={`px-2 py-0.5 text-xs rounded border ${styles[severity] || styles.medium}`}>
            {severity}
        </span>
    );
};

// Status badge
const StatusBadge = ({ status }) => {
    const styles = {
        open: 'bg-amber-500/10 text-amber-400',
        investigating: 'bg-blue-500/10 text-blue-400',
        assigned: 'bg-purple-500/10 text-purple-400',
        resolved: 'bg-emerald-500/10 text-emerald-400',
        dismissed: 'bg-slate-500/10 text-slate-400',
    };
    return (
        <span className={`px-2 py-0.5 text-xs rounded ${styles[status] || styles.open}`}>
            {status}
        </span>
    );
};

export default function ExceptionInbox() {
    const [loading, setLoading] = useState(true);
    const [exceptions, setExceptions] = useState([]);
    const [selectedException, setSelectedException] = useState(null);
    const [filters, setFilters] = useState({
        status: 'open',
        severity: '',
        type: ''
    });
    const [actionLoading, setActionLoading] = useState(false);

    const token = localStorage.getItem('token');

    const fetchExceptions = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (filters.status) params.append('status', filters.status);
            if (filters.severity) params.append('severity', filters.severity);
            if (filters.type) params.append('exception_type', filters.type);
            
            const res = await fetch(`${API_URL}/api/portfolio/exceptions?${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (res.ok) {
                const data = await res.json();
                setExceptions(data.exceptions || []);
            }
        } catch (err) {
            console.error('Error fetching exceptions:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (exceptionId, action, assignedTo = null) => {
        setActionLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/portfolio/exceptions/${exceptionId}/action`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action, assigned_to: assignedTo })
            });
            
            if (res.ok) {
                toast.success(`Exception ${action === 'approve' ? 'approved' : action === 'investigate' ? 'marked for investigation' : action}`);
                await fetchExceptions();
                setSelectedException(null);
            }
        } catch (err) {
            toast.error('Action failed');
        } finally {
            setActionLoading(false);
        }
    };

    useEffect(() => {
        fetchExceptions();
    }, [filters]);

    const formatAmount = (amount) => {
        if (!amount) return '-';
        return new Intl.NumberFormat('da-DK', { style: 'currency', currency: 'DKK' }).format(amount);
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleDateString('da-DK');
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Header */}
            <div className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center">
                                <Bell className="w-5 h-5 text-amber-500" />
                            </div>
                            <div>
                                <h1 className="font-medium text-white">Exception Inbox</h1>
                                <p className="text-xs text-slate-500">Transactions requiring review</p>
                            </div>
                        </div>
                        <Button 
                            variant="outline" 
                            size="sm"
                            onClick={fetchExceptions}
                            className="border-slate-700 text-slate-400 hover:text-white"
                        >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Refresh
                        </Button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Filters */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-slate-500" />
                        <span className="text-sm text-slate-500">Filters:</span>
                    </div>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters({...filters, status: e.target.value})}
                        className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2"
                    >
                        <option value="">All Status</option>
                        <option value="open">Open</option>
                        <option value="investigating">Investigating</option>
                        <option value="assigned">Assigned</option>
                        <option value="resolved">Resolved</option>
                        <option value="dismissed">Dismissed</option>
                    </select>
                    <select
                        value={filters.severity}
                        onChange={(e) => setFilters({...filters, severity: e.target.value})}
                        className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2"
                    >
                        <option value="">All Severity</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters({...filters, type: e.target.value})}
                        className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2"
                    >
                        <option value="">All Types</option>
                        <option value="expense_spike">Expense Spike</option>
                        <option value="duplicate_invoice">Duplicate Invoice</option>
                        <option value="unusual_vendor">Unusual Vendor</option>
                        <option value="vat_variance">VAT Variance</option>
                        <option value="pattern_deviation">Pattern Deviation</option>
                        <option value="vat_trend">VAT Trend</option>
                    </select>
                    <div className="ml-auto text-sm text-slate-500">
                        {exceptions.length} exception{exceptions.length !== 1 ? 's' : ''}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Exception List */}
                    <div className="space-y-3">
                        {loading ? (
                            <div className="text-slate-500 text-center py-12">Loading exceptions...</div>
                        ) : exceptions.length === 0 ? (
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-12 text-center">
                                <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-white mb-2">No Exceptions</h3>
                                <p className="text-slate-500">No exceptions match your current filters.</p>
                            </div>
                        ) : (
                            exceptions.map((exception) => (
                                <div
                                    key={exception.id}
                                    onClick={() => setSelectedException(exception)}
                                    className={`bg-slate-900/50 border rounded-xl p-4 cursor-pointer transition-all ${
                                        selectedException?.id === exception.id 
                                            ? 'border-emerald-500/50 ring-1 ring-emerald-500/20' 
                                            : 'border-slate-800 hover:border-slate-700'
                                    }`}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                                                exception.severity === 'high' ? 'bg-red-500/10 text-red-400' :
                                                exception.severity === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                                                'bg-slate-500/10 text-slate-400'
                                            }`}>
                                                <ExceptionIcon type={exception.type} />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium text-white">{exception.title}</div>
                                                <div className="text-xs text-slate-500">{exception.client_name}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <SeverityBadge severity={exception.severity} />
                                            <StatusBadge status={exception.status} />
                                        </div>
                                    </div>
                                    <p className="text-xs text-slate-400 line-clamp-2 mb-3">{exception.description}</p>
                                    <div className="flex items-center justify-between text-xs text-slate-500">
                                        <span>{formatAmount(exception.amount)}</span>
                                        <span>{formatDate(exception.detected_at)}</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Exception Detail Panel */}
                    <div className="lg:sticky lg:top-24 h-fit">
                        {selectedException ? (
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
                                <div className="p-6 border-b border-slate-800">
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <h3 className="text-lg font-medium text-white">{selectedException.title}</h3>
                                            <p className="text-sm text-slate-500">{selectedException.client_name}</p>
                                        </div>
                                        <button onClick={() => setSelectedException(null)} className="text-slate-500 hover:text-white">
                                            <X className="w-5 h-5" />
                                        </button>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <SeverityBadge severity={selectedException.severity} />
                                        <StatusBadge status={selectedException.status} />
                                    </div>
                                </div>
                                
                                <div className="p-6 space-y-6">
                                    {/* Transaction Details */}
                                    {selectedException.amount && (
                                        <div className="bg-slate-800/30 rounded-lg p-4 space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-slate-500">Amount</span>
                                                <span className="text-white font-medium">{formatAmount(selectedException.amount)}</span>
                                            </div>
                                            {selectedException.vendor && (
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-slate-500">Vendor</span>
                                                    <span className="text-slate-300">{selectedException.vendor}</span>
                                                </div>
                                            )}
                                            {selectedException.account_code && (
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-slate-500">Account</span>
                                                    <span className="text-slate-300">{selectedException.account_code} - {selectedException.account_name}</span>
                                                </div>
                                            )}
                                            {selectedException.transaction_date && (
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-slate-500">Date</span>
                                                    <span className="text-slate-300">{formatDate(selectedException.transaction_date)}</span>
                                                </div>
                                            )}
                                            {selectedException.historical_avg && (
                                                <div className="flex justify-between text-sm border-t border-slate-700 pt-2 mt-2">
                                                    <span className="text-slate-500">Historical Average</span>
                                                    <span className="text-slate-300">{formatAmount(selectedException.historical_avg)}</span>
                                                </div>
                                            )}
                                            {selectedException.variance_percent && (
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-slate-500">Variance</span>
                                                    <span className="text-red-400">+{selectedException.variance_percent.toFixed(0)}%</span>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                    
                                    {/* Analysis */}
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Analysis</div>
                                        <p className="text-sm text-slate-300 leading-relaxed">{selectedException.description}</p>
                                    </div>
                                    
                                    {/* Actions */}
                                    {selectedException.status === 'open' && (
                                        <div className="flex gap-3 pt-4 border-t border-slate-800">
                                            <Button
                                                size="sm"
                                                onClick={() => handleAction(selectedException.id, 'approve')}
                                                disabled={actionLoading}
                                                className="bg-emerald-600 hover:bg-emerald-500 flex-1"
                                            >
                                                <CheckCircle className="w-4 h-4 mr-2" />
                                                Approve
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleAction(selectedException.id, 'investigate')}
                                                disabled={actionLoading}
                                                className="border-slate-700 text-slate-300 flex-1"
                                            >
                                                <Eye className="w-4 h-4 mr-2" />
                                                Investigate
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleAction(selectedException.id, 'dismiss')}
                                                disabled={actionLoading}
                                                className="border-slate-700 text-slate-300"
                                            >
                                                <X className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-12 text-center">
                                <Eye className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-white mb-2">Select an Exception</h3>
                                <p className="text-slate-500">Click on an exception to view details and take action.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
