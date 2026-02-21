import React, { useState, useEffect } from 'react';
import { 
    Shield, 
    AlertTriangle, 
    Clock, 
    Users, 
    ChevronRight,
    ArrowUpDown,
    Filter,
    RefreshCw,
    Building2,
    CheckCircle,
    XCircle,
    Search
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Risk level badge component
const RiskBadge = ({ level }) => {
    const styles = {
        high: 'bg-red-500/10 text-red-400 border-red-500/20',
        elevated: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        normal: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };
    
    const labels = {
        high: 'High Risk',
        elevated: 'Elevated',
        normal: 'Normal',
    };
    
    return (
        <span className={`px-2 py-1 text-xs rounded border ${styles[level] || styles.normal}`}>
            {labels[level] || level}
        </span>
    );
};

// Risk indicator dot
const RiskDot = ({ level }) => {
    const colors = {
        high: 'bg-red-500',
        elevated: 'bg-amber-500',
        normal: 'bg-emerald-500',
    };
    return <div className={`w-2 h-2 rounded-full ${colors[level] || colors.normal}`}></div>;
};

export default function PortfolioRiskDashboard() {
    const [loading, setLoading] = useState(true);
    const [summary, setSummary] = useState(null);
    const [clients, setClients] = useState([]);
    const [sortBy, setSortBy] = useState('risk_score');
    const [sortOrder, setSortOrder] = useState('desc');
    const [searchTerm, setSearchTerm] = useState('');
    const [generatingData, setGeneratingData] = useState(false);

    const token = localStorage.getItem('token');

    const fetchData = async () => {
        setLoading(true);
        try {
            const headers = { 'Authorization': `Bearer ${token}` };
            
            // Fetch summary and clients in parallel
            const [summaryRes, clientsRes] = await Promise.all([
                fetch(`${API_URL}/api/portfolio/summary`, { headers }),
                fetch(`${API_URL}/api/portfolio/clients?sort_by=${sortBy}&sort_order=${sortOrder}`, { headers })
            ]);
            
            if (summaryRes.ok && clientsRes.ok) {
                const summaryData = await summaryRes.json();
                const clientsData = await clientsRes.json();
                setSummary(summaryData);
                setClients(clientsData.clients || []);
            }
        } catch (err) {
            console.error('Error fetching portfolio data:', err);
        } finally {
            setLoading(false);
        }
    };

    const generateDemoData = async () => {
        setGeneratingData(true);
        try {
            const res = await fetch(`${API_URL}/api/portfolio/generate-demo-data`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                toast.success(`Demo data generated: ${data.stats.clients} clients, ${data.stats.exceptions} exceptions`);
                await fetchData();
            } else {
                toast.info(data.message || 'Demo data already exists');
            }
        } catch (err) {
            toast.error('Failed to generate demo data');
        } finally {
            setGeneratingData(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [sortBy, sortOrder]);

    const handleSort = (field) => {
        if (sortBy === field) {
            setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
        } else {
            setSortBy(field);
            setSortOrder('desc');
        }
    };

    const filteredClients = clients.filter(client => 
        client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.cvr?.includes(searchTerm)
    );

    if (loading && !summary) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-slate-400">Loading portfolio data...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Header */}
            <div className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-emerald-500" />
                            </div>
                            <div>
                                <h1 className="font-medium text-white">Portfolio Risk Dashboard</h1>
                                <p className="text-xs text-slate-500">Client portfolio overview</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Button 
                                variant="outline" 
                                size="sm"
                                onClick={fetchData}
                                className="border-slate-700 text-slate-400 hover:text-white"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh
                            </Button>
                            {clients.length === 0 && (
                                <Button 
                                    size="sm"
                                    onClick={generateDemoData}
                                    disabled={generatingData}
                                    className="bg-emerald-600 hover:bg-emerald-500"
                                >
                                    {generatingData ? 'Generating...' : 'Generate Demo Data'}
                                </Button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-white">{summary?.total_clients || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">Total Clients</div>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-red-400">{summary?.high_risk || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">High Risk</div>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-amber-400">{summary?.elevated_risk || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">Elevated Risk</div>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-emerald-400">{summary?.normal_risk || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">Normal</div>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-white">{summary?.open_exceptions || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">Open Exceptions</div>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                        <div className="text-2xl font-semibold text-white">{summary?.clients_near_vat_deadline || 0}</div>
                        <div className="text-xs text-slate-500 mt-1">Near VAT Deadline</div>
                    </div>
                </div>

                {/* Search and Filters */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <Input
                            placeholder="Search clients by name or CVR..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-10 bg-slate-900/50 border-slate-800 text-white placeholder:text-slate-600"
                        />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <span>Sort:</span>
                        <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleSort('risk_score')}
                            className={`text-xs ${sortBy === 'risk_score' ? 'text-white' : 'text-slate-500'}`}
                        >
                            Risk Score
                            <ArrowUpDown className="w-3 h-3 ml-1" />
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleSort('days_to_vat_deadline')}
                            className={`text-xs ${sortBy === 'days_to_vat_deadline' ? 'text-white' : 'text-slate-500'}`}
                        >
                            VAT Deadline
                            <ArrowUpDown className="w-3 h-3 ml-1" />
                        </Button>
                        <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleSort('exception_count')}
                            className={`text-xs ${sortBy === 'exception_count' ? 'text-white' : 'text-slate-500'}`}
                        >
                            Exceptions
                            <ArrowUpDown className="w-3 h-3 ml-1" />
                        </Button>
                    </div>
                </div>

                {/* Client List */}
                {clients.length === 0 ? (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-12 text-center">
                        <Building2 className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-white mb-2">No Client Data</h3>
                        <p className="text-slate-500 mb-6 max-w-md mx-auto">
                            Generate demo data to see the portfolio risk dashboard in action with realistic Danish client companies.
                        </p>
                        <Button 
                            onClick={generateDemoData}
                            disabled={generatingData}
                            className="bg-emerald-600 hover:bg-emerald-500"
                        >
                            {generatingData ? 'Generating...' : 'Generate Demo Portfolio'}
                        </Button>
                    </div>
                ) : (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-800">
                                    <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-4">Client</th>
                                    <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-4">Risk Level</th>
                                    <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-4">Exceptions</th>
                                    <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-4">VAT Deadline</th>
                                    <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-4">Assigned To</th>
                                    <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-4"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {filteredClients.map((client) => (
                                    <tr 
                                        key={client.id} 
                                        className="hover:bg-slate-800/30 transition-colors cursor-pointer"
                                        onClick={() => window.location.href = `/app/portfolio/client/${client.id}`}
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <RiskDot level={client.risk_level} />
                                                <div>
                                                    <div className="text-sm font-medium text-white">{client.name}</div>
                                                    <div className="text-xs text-slate-500">CVR: {client.cvr}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <RiskBadge level={client.risk_level} />
                                        </td>
                                        <td className="px-4 py-4">
                                            {client.open_exceptions > 0 ? (
                                                <span className="text-amber-400 text-sm">{client.open_exceptions} open</span>
                                            ) : (
                                                <span className="text-slate-500 text-sm">None</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className={`text-sm ${client.days_to_vat_deadline <= 14 ? 'text-amber-400' : 'text-slate-400'}`}>
                                                {client.days_to_vat_deadline} days
                                            </div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="text-sm text-slate-400">{client.assigned_staff}</div>
                                            <div className="text-xs text-slate-600">{client.staff_role}</div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <ChevronRight className="w-4 h-4 text-slate-600 inline" />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
