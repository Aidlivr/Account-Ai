import React, { useState, useEffect } from 'react';
import { 
    Clock, 
    AlertTriangle, 
    CheckCircle,
    ChevronRight,
    RefreshCw,
    Calendar,
    Shield,
    FileCheck,
    XCircle,
    Building2
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Checklist item component
const ChecklistItem = ({ label, checked, critical = false }) => (
    <div className="flex items-center gap-3 py-2">
        {checked ? (
            <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
        ) : (
            <XCircle className={`w-4 h-4 flex-shrink-0 ${critical ? 'text-red-400' : 'text-amber-400'}`} />
        )}
        <span className={`text-sm ${checked ? 'text-slate-400' : critical ? 'text-red-400' : 'text-amber-400'}`}>
            {label}
        </span>
    </div>
);

// Client VAT status card
const ClientVATCard = ({ client, onViewDetail }) => {
    const daysLeft = client.days_to_vat_deadline;
    const urgency = daysLeft <= 7 ? 'critical' : daysLeft <= 14 ? 'warning' : 'normal';
    
    const urgencyStyles = {
        critical: 'border-red-500/30 bg-red-500/5',
        warning: 'border-amber-500/30 bg-amber-500/5',
        normal: 'border-slate-800',
    };
    
    const checklist = client.vat_checklist || {};
    const checklistItems = [
        { key: 'exceptions_reviewed', label: 'All exceptions reviewed', critical: true },
        { key: 'no_high_risk_items', label: 'No high-risk items pending', critical: true },
        { key: 'recent_review', label: 'Reviewed within 7 days', critical: false },
        { key: 'vat_trends_checked', label: 'VAT trends verified', critical: false },
    ];
    
    const completedCount = checklistItems.filter(item => checklist[item.key]).length;
    const progress = (completedCount / checklistItems.length) * 100;
    
    return (
        <div className={`bg-slate-900/50 border rounded-xl overflow-hidden ${urgencyStyles[urgency]}`}>
            <div className="p-5">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <h3 className="font-medium text-white">{client.name}</h3>
                        <p className="text-xs text-slate-500">CVR: {client.cvr}</p>
                    </div>
                    <div className={`text-right ${
                        urgency === 'critical' ? 'text-red-400' :
                        urgency === 'warning' ? 'text-amber-400' : 'text-slate-400'
                    }`}>
                        <div className="text-2xl font-semibold">{daysLeft}</div>
                        <div className="text-xs">days left</div>
                    </div>
                </div>
                
                {/* Progress bar */}
                <div className="mb-4">
                    <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-500">Pre-VAT Checklist</span>
                        <span className={client.vat_ready ? 'text-emerald-400' : 'text-amber-400'}>
                            {completedCount}/{checklistItems.length}
                        </span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div 
                            className={`h-full rounded-full transition-all ${client.vat_ready ? 'bg-emerald-500' : 'bg-amber-500'}`}
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
                
                {/* Checklist */}
                <div className="border-t border-slate-800 pt-3 space-y-1">
                    {checklistItems.map((item) => (
                        <ChecklistItem 
                            key={item.key}
                            label={item.label}
                            checked={checklist[item.key]}
                            critical={item.critical}
                        />
                    ))}
                </div>
                
                {/* Open exceptions summary */}
                {client.open_exceptions > 0 && (
                    <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                        <div className="flex items-center gap-2 text-amber-400 text-sm">
                            <AlertTriangle className="w-4 h-4" />
                            <span>{client.open_exceptions} open exception{client.open_exceptions > 1 ? 's' : ''} requiring review</span>
                        </div>
                    </div>
                )}
            </div>
            
            <div className="px-5 py-3 bg-slate-800/30 border-t border-slate-800 flex items-center justify-between">
                <span className={`text-xs font-medium ${client.vat_ready ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {client.vat_ready ? 'Ready for VAT submission' : 'Action required'}
                </span>
                <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onViewDetail(client)}
                    className="text-slate-400 hover:text-white text-xs"
                >
                    View Details
                    <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
            </div>
        </div>
    );
};

export default function PreVATReview() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [daysThreshold, setDaysThreshold] = useState(30);
    const [selectedClient, setSelectedClient] = useState(null);

    const token = localStorage.getItem('token');

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/portfolio/pre-vat-review?days=${daysThreshold}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (res.ok) {
                const result = await res.json();
                setData(result);
            }
        } catch (err) {
            console.error('Error fetching pre-VAT data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [daysThreshold]);

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleDateString('da-DK', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Header */}
            <div className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center">
                                <Clock className="w-5 h-5 text-emerald-500" />
                            </div>
                            <div>
                                <h1 className="font-medium text-white">Pre-VAT Review Mode</h1>
                                <p className="text-xs text-slate-500">Clients approaching VAT deadline</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <select
                                value={daysThreshold}
                                onChange={(e) => setDaysThreshold(parseInt(e.target.value))}
                                className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2"
                            >
                                <option value={14}>Next 14 days</option>
                                <option value={30}>Next 30 days</option>
                                <option value={60}>Next 60 days</option>
                            </select>
                            <Button 
                                variant="outline" 
                                size="sm"
                                onClick={fetchData}
                                className="border-slate-700 text-slate-400 hover:text-white"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {loading ? (
                    <div className="text-slate-500 text-center py-12">Loading pre-VAT review data...</div>
                ) : !data || data.total_clients === 0 ? (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-12 text-center">
                        <Calendar className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-white mb-2">No Upcoming Deadlines</h3>
                        <p className="text-slate-500 max-w-md mx-auto">
                            No clients have VAT deadlines within the next {daysThreshold} days.
                        </p>
                    </div>
                ) : (
                    <>
                        {/* Summary */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <Building2 className="w-5 h-5 text-slate-500" />
                                    <span className="text-sm text-slate-500">Total Clients</span>
                                </div>
                                <div className="text-3xl font-semibold text-white">{data.total_clients}</div>
                            </div>
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                                    <span className="text-sm text-slate-500">Ready</span>
                                </div>
                                <div className="text-3xl font-semibold text-emerald-400">{data.ready_count}</div>
                            </div>
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                                    <span className="text-sm text-slate-500">Needs Attention</span>
                                </div>
                                <div className="text-3xl font-semibold text-amber-400">{data.needs_attention}</div>
                            </div>
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
                                <div className="flex items-center gap-3 mb-3">
                                    <Shield className="w-5 h-5 text-slate-500" />
                                    <span className="text-sm text-slate-500">Readiness Rate</span>
                                </div>
                                <div className="text-3xl font-semibold text-white">
                                    {data.total_clients > 0 ? Math.round((data.ready_count / data.total_clients) * 100) : 0}%
                                </div>
                            </div>
                        </div>

                        {/* Timeline indicator */}
                        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-8">
                            <div className="flex items-center justify-between text-sm">
                                <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-slate-500" />
                                    <span className="text-slate-400">VAT Deadline Timeline</span>
                                </div>
                                <div className="flex items-center gap-6">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded bg-red-500"></div>
                                        <span className="text-slate-500">Critical (&lt;7 days)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded bg-amber-500"></div>
                                        <span className="text-slate-500">Warning (&lt;14 days)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded bg-slate-600"></div>
                                        <span className="text-slate-500">Normal</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Client cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {data.clients?.map((client) => (
                                <ClientVATCard
                                    key={client.id}
                                    client={client}
                                    onViewDetail={setSelectedClient}
                                />
                            ))}
                        </div>
                    </>
                )}
            </div>

            {/* Client Detail Modal */}
            {selectedClient && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
                        <div className="p-6 border-b border-slate-800">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h2 className="text-xl font-medium text-white">{selectedClient.name}</h2>
                                    <p className="text-sm text-slate-500">Pre-VAT Review Details</p>
                                </div>
                                <button 
                                    onClick={() => setSelectedClient(null)}
                                    className="text-slate-500 hover:text-white"
                                >
                                    ✕
                                </button>
                            </div>
                        </div>
                        <div className="p-6">
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-slate-800/50 rounded-lg p-4">
                                    <div className="text-xs text-slate-500 mb-1">VAT Deadline</div>
                                    <div className="text-white">{formatDate(selectedClient.vat_deadline)}</div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4">
                                    <div className="text-xs text-slate-500 mb-1">Days Remaining</div>
                                    <div className={`text-xl font-semibold ${
                                        selectedClient.days_to_vat_deadline <= 7 ? 'text-red-400' :
                                        selectedClient.days_to_vat_deadline <= 14 ? 'text-amber-400' : 'text-white'
                                    }`}>
                                        {selectedClient.days_to_vat_deadline} days
                                    </div>
                                </div>
                            </div>
                            
                            {selectedClient.open_exceptions_list?.length > 0 && (
                                <div className="mb-6">
                                    <h3 className="text-sm font-medium text-white mb-3">Open Exceptions</h3>
                                    <div className="space-y-2">
                                        {selectedClient.open_exceptions_list.map((exc) => (
                                            <div key={exc.id} className="bg-slate-800/50 rounded-lg p-3 flex items-center justify-between">
                                                <div>
                                                    <div className="text-sm text-white">{exc.title}</div>
                                                    <div className="text-xs text-slate-500">{exc.type}</div>
                                                </div>
                                                <span className={`px-2 py-0.5 text-xs rounded ${
                                                    exc.severity === 'high' ? 'bg-red-500/10 text-red-400' :
                                                    exc.severity === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                                                    'bg-slate-500/10 text-slate-400'
                                                }`}>
                                                    {exc.severity}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            <div className="flex justify-end gap-3">
                                <Button
                                    variant="outline"
                                    onClick={() => setSelectedClient(null)}
                                    className="border-slate-700 text-slate-400"
                                >
                                    Close
                                </Button>
                                <Button
                                    onClick={() => {
                                        window.location.href = `/app/portfolio/exceptions?client_id=${selectedClient.id}`;
                                    }}
                                    className="bg-emerald-600 hover:bg-emerald-500"
                                >
                                    Review Exceptions
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
