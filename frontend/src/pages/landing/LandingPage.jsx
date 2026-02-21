import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
    Shield, 
    AlertTriangle,
    TrendingUp,
    Users, 
    Clock,
    ArrowRight,
    Building2,
    Eye,
    Layers,
    Target,
    CheckCircle,
    BarChart3,
    Bell,
    Filter,
    Zap,
    Lock,
    FileSearch,
    UserCheck,
    ChevronRight
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Beta request form submission
const submitBetaRequest = async (formData) => {
    const response = await fetch(`${API_URL}/api/beta/request-access`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            firm_name: formData.firmName,
            contact_person: formData.contactPerson,
            email: formData.email,
            active_clients: formData.activeClients
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Submission failed');
    }
    
    return response.json();
};

export default function LandingPage() {
    const [betaForm, setBetaForm] = useState({
        firmName: '',
        contactPerson: '',
        email: '',
        activeClients: ''
    });
    const [submitting, setSubmitting] = useState(false);

    const handleBetaSubmit = async (e) => {
        e.preventDefault();
        if (!betaForm.firmName || !betaForm.email) {
            toast.error('Please fill in required fields');
            return;
        }
        setSubmitting(true);
        try {
            const result = await submitBetaRequest(betaForm);
            if (result.already_registered) {
                toast.info('You have already requested access. We will contact you shortly.');
            } else {
                toast.success('Thank you for your interest. We will contact you shortly.');
            }
            setBetaForm({ firmName: '', contactPerson: '', email: '', activeClients: '' });
        } catch (err) {
            toast.error(err.message || 'Submission failed. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Navigation */}
            <nav className="border-b border-slate-800/50 bg-slate-950/95 backdrop-blur-sm sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-emerald-500" />
                            </div>
                            <span className="font-medium text-white text-lg tracking-tight">Accountrix</span>
                        </div>
                        <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
                            <a href="#platform" className="hover:text-white transition-colors">Platform</a>
                            <a href="#capabilities" className="hover:text-white transition-colors">Capabilities</a>
                            <a href="#approach" className="hover:text-white transition-colors">Approach</a>
                            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
                        </div>
                        <div className="flex items-center gap-3">
                            <Link to="/login">
                                <Button variant="ghost" className="text-slate-400 hover:text-white hover:bg-slate-800">
                                    Sign In
                                </Button>
                            </Link>
                            <a href="#contact">
                                <Button className="bg-emerald-600 hover:bg-emerald-500 text-white">
                                    Request Demo
                                </Button>
                            </a>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative">
                <div className="max-w-6xl mx-auto px-6 py-24 lg:py-28">
                    <div className="max-w-3xl">
                        <h1 className="text-4xl lg:text-5xl font-medium text-white leading-tight mb-6 tracking-tight">
                            Professional Control Across Your Entire Client Portfolio
                        </h1>
                        <p className="text-lg text-slate-400 mb-6 leading-relaxed max-w-2xl">
                            A control and risk intelligence layer for accounting firms managing large client portfolios. 
                            Gain cross-client visibility, surface exceptions that require attention, and ensure 
                            pre-VAT review completeness—without replacing your existing accounting systems.
                        </p>
                        
                        {/* Positioning clarity */}
                        <p className="text-sm text-slate-500 mb-10 flex items-center gap-2">
                            <span className="w-1 h-1 bg-slate-600 rounded-full"></span>
                            Works alongside your existing accounting system. No replacement. No disruption.
                        </p>
                        
                        <div className="flex flex-col sm:flex-row gap-4 mb-16">
                            <a href="#contact">
                                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-500 text-white px-8">
                                    Schedule a Consultation
                                    <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            </a>
                            <a href="#platform">
                                <Button size="lg" variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white px-8">
                                    Learn More
                                </Button>
                            </a>
                        </div>
                        
                        {/* Professional Metrics */}
                        <div className="grid grid-cols-3 gap-8 pt-10 border-t border-slate-800">
                            <div>
                                <div className="text-sm font-medium text-white mb-1">Portfolio-Wide</div>
                                <div className="text-sm text-slate-500">Risk Visibility</div>
                            </div>
                            <div>
                                <div className="text-sm font-medium text-white mb-1">Intelligent</div>
                                <div className="text-sm text-slate-500">Exception Prioritization</div>
                            </div>
                            <div>
                                <div className="text-sm font-medium text-white mb-1">Pre-VAT</div>
                                <div className="text-sm text-slate-500">Anomaly Detection</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Hero Visual - Risk Overview */}
                <div className="absolute right-0 top-24 w-[45%] hidden xl:block">
                    <div className="bg-slate-900/80 rounded-l-xl border border-slate-800 p-6">
                        <div className="flex items-center justify-between mb-5">
                            <span className="text-sm font-medium text-slate-300">Client Risk Overview</span>
                            <span className="text-xs text-slate-600">Updated continuously</span>
                        </div>
                        <div className="space-y-2">
                            {[
                                { client: 'Nordisk Handel ApS', risk: 'elevated', flags: 3, vat: '12 days' },
                                { client: 'TechStart Denmark', risk: 'moderate', flags: 1, vat: '12 days' },
                                { client: 'Café Strøget IVS', risk: 'normal', flags: 0, vat: '12 days' },
                                { client: 'Maritime Solutions', risk: 'elevated', flags: 5, vat: '12 days' },
                                { client: 'Green Energy DK', risk: 'normal', flags: 0, vat: '12 days' },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between bg-slate-800/40 rounded-lg px-4 py-3 border border-slate-800/50">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${
                                            item.risk === 'elevated' ? 'bg-amber-500' : 
                                            item.risk === 'moderate' ? 'bg-slate-400' : 'bg-emerald-500'
                                        }`}></div>
                                        <span className="text-sm text-slate-300">{item.client}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        {item.flags > 0 && (
                                            <span className="text-xs text-slate-500">
                                                {item.flags} exception{item.flags > 1 ? 's' : ''}
                                            </span>
                                        )}
                                        <span className="text-xs text-slate-600">VAT: {item.vat}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Problem Statement Section */}
            <section id="platform" className="py-24 bg-slate-900/30">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-16">
                        <h2 className="text-2xl lg:text-3xl font-medium text-white mb-4">
                            Your System Shows Every Transaction. You Need to See What Matters.
                        </h2>
                        <p className="text-slate-400">
                            When you're responsible for hundreds of clients, comprehensive visibility requires more than transaction logs. 
                            It requires intelligent prioritization.
                        </p>
                    </div>
                    
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {[
                            {
                                icon: Eye,
                                title: 'Cross-Client Visibility',
                                description: 'Accounting systems show data per client. Managing 100+ clients requires portfolio-wide oversight to identify where attention is needed.'
                            },
                            {
                                icon: TrendingUp,
                                title: 'Pattern Recognition',
                                description: 'Unusual expense patterns, VAT fluctuations, or posting anomalies often indicate issues that require review before they compound.'
                            },
                            {
                                icon: Clock,
                                title: 'VAT Period Preparation',
                                description: 'Pre-submission review across a large portfolio benefits from systematic prioritization rather than uniform checking.'
                            },
                            {
                                icon: Users,
                                title: 'Staff Work Review',
                                description: 'When multiple team members handle bookkeeping, identifying which entries warrant senior review improves quality control.'
                            },
                            {
                                icon: FileSearch,
                                title: 'Exception Identification',
                                description: 'Duplicate entries, unusual vendor activity, and classification deviations are easier to address when surfaced systematically.'
                            },
                            {
                                icon: Layers,
                                title: 'System Complementarity',
                                description: 'Your accounting system manages transactions. This platform provides the analytical layer for risk assessment and prioritization.'
                            }
                        ].map((item, i) => (
                            <div key={i} className="bg-slate-800/30 border border-slate-800/50 rounded-xl p-6">
                                <item.icon className="w-6 h-6 text-slate-500 mb-4" />
                                <h3 className="font-medium text-white mb-2 text-sm">{item.title}</h3>
                                <p className="text-sm text-slate-500 leading-relaxed">{item.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Architecture Positioning */}
            <section id="approach" className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        <div>
                            <div className="text-sm text-slate-500 mb-4 uppercase tracking-wider">Architecture</div>
                            <h2 className="text-2xl lg:text-3xl font-medium text-white mb-6">
                                A Control Layer Above Your Existing Systems
                            </h2>
                            <p className="text-slate-400 mb-8 leading-relaxed">
                                Accountrix operates alongside your accounting software—e-conomic, Dinero, Fortnox, or others. 
                                We connect via secure API to provide risk analysis and exception detection without 
                                interfering with your established workflows.
                            </p>
                            <div className="space-y-4">
                                {[
                                    { label: 'No system replacement', desc: 'Your accounting software remains your source of truth.' },
                                    { label: 'No workflow disruption', desc: 'Your team continues working as before.' },
                                    { label: 'Portfolio-level analysis', desc: 'Cross-client intelligence that individual systems cannot provide.' },
                                ].map((item, i) => (
                                    <div key={i} className="flex items-start gap-3">
                                        <CheckCircle className="w-4 h-4 text-emerald-500 mt-1 flex-shrink-0" />
                                        <div>
                                            <span className="text-white text-sm">{item.label}</span>
                                            <span className="text-slate-500 text-sm"> — {item.desc}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        {/* Architecture Diagram */}
                        <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-8">
                            <div className="space-y-4">
                                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 text-center">
                                    <Shield className="w-5 h-5 text-emerald-500 mx-auto mb-2" />
                                    <div className="text-white font-medium text-sm">Accountrix</div>
                                    <div className="text-xs text-slate-500">Control & Risk Intelligence</div>
                                </div>
                                <div className="flex justify-center">
                                    <div className="w-px h-6 bg-slate-700"></div>
                                </div>
                                <div className="text-center text-xs text-slate-600 py-1">
                                    Secure API Integration
                                </div>
                                <div className="flex justify-center">
                                    <div className="w-px h-6 bg-slate-700"></div>
                                </div>
                                <div className="grid grid-cols-3 gap-3">
                                    {['e-conomic', 'Dinero', 'Fortnox'].map((sys, i) => (
                                        <div key={i} className="bg-slate-800/30 border border-slate-800/50 rounded-lg p-3 text-center">
                                            <Building2 className="w-4 h-4 text-slate-600 mx-auto mb-1" />
                                            <div className="text-xs text-slate-500">{sys}</div>
                                        </div>
                                    ))}
                                </div>
                                <div className="text-center text-xs text-slate-600 mt-2">
                                    Your existing accounting systems
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Capabilities */}
            <section id="capabilities" className="py-24 bg-slate-900/30">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <div className="text-sm text-slate-500 mb-4 uppercase tracking-wider">Capabilities</div>
                        <h2 className="text-2xl lg:text-3xl font-medium text-white mb-4">
                            Three Core Modules for Portfolio Oversight
                        </h2>
                        <p className="text-slate-400 max-w-2xl mx-auto">
                            Designed for partners and senior reviewers responsible for maintaining quality 
                            and compliance across large client portfolios.
                        </p>
                    </div>
                    
                    <div className="grid lg:grid-cols-3 gap-6">
                        {/* Module 1 */}
                        <div className="bg-slate-800/30 border border-slate-800/50 rounded-xl p-8">
                            <div className="w-10 h-10 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center mb-6">
                                <Target className="w-5 h-5 text-amber-500" />
                            </div>
                            <h3 className="text-lg font-medium text-white mb-3">Portfolio Risk Dashboard</h3>
                            <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                                A consolidated view of all clients with risk indicators, enabling rapid identification of accounts requiring attention.
                            </p>
                            <ul className="space-y-2">
                                {[
                                    'Client-level risk assessment',
                                    'VAT trend monitoring',
                                    'Expense pattern analysis',
                                    'Duplicate detection',
                                    'Documentation status'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                        <ChevronRight className="w-3 h-3 text-slate-600" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        {/* Module 2 */}
                        <div className="bg-slate-800/30 border border-slate-800/50 rounded-xl p-8">
                            <div className="w-10 h-10 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center mb-6">
                                <Bell className="w-5 h-5 text-slate-400" />
                            </div>
                            <h3 className="text-lg font-medium text-white mb-3">Exception Inbox</h3>
                            <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                                Prioritized queue of transactions and patterns that deviate from established norms, with context for informed review.
                            </p>
                            <ul className="space-y-2">
                                {[
                                    'Pattern deviation alerts',
                                    'High-impact transaction flags',
                                    'Vendor activity monitoring',
                                    'Classification review items',
                                    'Contextual explanations'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                        <ChevronRight className="w-3 h-3 text-slate-600" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        {/* Module 3 */}
                        <div className="bg-slate-800/30 border border-slate-800/50 rounded-xl p-8">
                            <div className="w-10 h-10 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center mb-6">
                                <Clock className="w-5 h-5 text-emerald-500" />
                            </div>
                            <h3 className="text-lg font-medium text-white mb-3">Pre-VAT Review Mode</h3>
                            <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                                Structured review workflow as VAT deadlines approach, ensuring systematic coverage of compliance-relevant items.
                            </p>
                            <ul className="space-y-2">
                                {[
                                    'Period-over-period comparison',
                                    'VAT rate variance detection',
                                    'Deduction pattern analysis',
                                    'Missing entry identification',
                                    'Pre-submission checklist'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                        <ChevronRight className="w-3 h-3 text-slate-600" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* Exception Detail Example */}
            <section className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
                            <div className="text-xs text-slate-600 mb-4 uppercase tracking-wider">Exception Detail</div>
                            <div className="bg-slate-800/30 rounded-lg p-5 mb-4 border border-slate-800/50">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <div className="text-white text-sm font-medium">Expense Variance Detected</div>
                                        <div className="text-slate-500 text-xs mt-1">Nordisk Handel ApS</div>
                                    </div>
                                    <span className="px-2 py-1 bg-amber-500/10 text-amber-500 text-xs rounded border border-amber-500/20">Review Recommended</span>
                                </div>
                                <div className="space-y-2 text-sm border-t border-slate-800/50 pt-4">
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Transaction</span>
                                        <span className="text-slate-300">Office Equipment — 47,500 DKK</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">12-month average</span>
                                        <span className="text-slate-300">3,200 DKK</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Variance</span>
                                        <span className="text-amber-500">+1,384%</span>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-slate-800/20 rounded-lg p-4 border border-slate-800/30">
                                <div className="text-xs text-slate-600 mb-2">Analysis</div>
                                <p className="text-sm text-slate-400 leading-relaxed">
                                    This expense significantly exceeds the historical average for account 6310 (IT Equipment). 
                                    Similar entries in the past were classified as capital expenditures. 
                                    Consider verifying asset classification and depreciation treatment.
                                </p>
                            </div>
                            <div className="flex gap-3 mt-5">
                                <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs">Mark Reviewed</Button>
                                <Button size="sm" variant="outline" className="border-slate-700 text-slate-400 hover:text-white text-xs">Investigate</Button>
                                <Button size="sm" variant="outline" className="border-slate-700 text-slate-400 hover:text-white text-xs">Assign</Button>
                            </div>
                        </div>
                        
                        <div>
                            <div className="text-sm text-slate-500 mb-4 uppercase tracking-wider">Transparency</div>
                            <h2 className="text-2xl lg:text-3xl font-medium text-white mb-6">
                                Every Flag Includes Full Context
                            </h2>
                            <p className="text-slate-400 mb-8 leading-relaxed">
                                Each exception presented by the system includes the underlying data, historical comparison, 
                                and reasoning. Decisions remain with your team—the platform provides analysis, not conclusions.
                            </p>
                            <div className="space-y-4">
                                {[
                                    { icon: Eye, text: 'Clear explanation for every flag' },
                                    { icon: BarChart3, text: 'Historical data for context' },
                                    { icon: FileSearch, text: 'Full audit trail maintained' },
                                    { icon: UserCheck, text: 'Human review required for all actions' },
                                ].map((item, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="w-8 h-8 bg-slate-800/50 border border-slate-800 rounded-lg flex items-center justify-center">
                                            <item.icon className="w-4 h-4 text-slate-500" />
                                        </div>
                                        <span className="text-slate-400 text-sm">{item.text}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-24 bg-slate-900/30">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <div className="text-sm text-slate-500 mb-4 uppercase tracking-wider">Pricing</div>
                        <h2 className="text-2xl lg:text-3xl font-medium text-white mb-4">
                            Firm-Level Pricing
                        </h2>
                        <p className="text-slate-400">
                            Straightforward pricing based on your portfolio size. No per-transaction or per-invoice charges.
                        </p>
                    </div>
                    
                    <div className="max-w-md mx-auto">
                        <div className="bg-slate-800/30 border border-slate-800/50 rounded-xl overflow-hidden">
                            <div className="bg-slate-800/50 px-8 py-6 border-b border-slate-800/50">
                                <h3 className="text-white font-medium text-lg">Professional</h3>
                                <p className="text-slate-500 text-sm mt-1">For firms managing 50–300+ clients</p>
                            </div>
                            <div className="p-8">
                                <div className="text-center mb-8">
                                    <div className="text-slate-500 text-sm mb-2">Starting from</div>
                                    <div className="flex items-baseline justify-center gap-1">
                                        <span className="text-3xl font-medium text-white">2.499</span>
                                        <span className="text-slate-500">DKK / month</span>
                                    </div>
                                    <p className="text-slate-600 text-sm mt-2">
                                        Includes up to 100 connected clients
                                    </p>
                                </div>
                                
                                <div className="bg-slate-800/30 rounded-lg p-4 mb-8 border border-slate-800/50">
                                    <div className="text-center">
                                        <span className="text-slate-500 text-sm">Additional clients:</span>
                                        <span className="text-white text-sm ml-2">+15 DKK / client / month</span>
                                    </div>
                                </div>
                                
                                <ul className="space-y-3 mb-8">
                                    {[
                                        'Portfolio Risk Dashboard',
                                        'Exception Inbox',
                                        'Pre-VAT Review Mode',
                                        'Unlimited users',
                                        'e-conomic integration',
                                        'Transaction Intelligence',
                                        'Priority support'
                                    ].map((item, i) => (
                                        <li key={i} className="flex items-center gap-3 text-slate-400">
                                            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                                            <span className="text-sm">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                
                                <a href="#contact" className="block">
                                    <Button className="w-full bg-emerald-600 hover:bg-emerald-500 text-white">
                                        Request Demo
                                    </Button>
                                </a>
                            </div>
                        </div>
                        
                        <p className="text-center text-sm text-slate-600 mt-6">
                            Enterprise pricing available for larger portfolios.
                        </p>
                    </div>
                </div>
            </section>

            {/* Contact Section */}
            <section id="contact" className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-xl mx-auto">
                        <div className="text-center mb-10">
                            <h2 className="text-2xl lg:text-3xl font-medium text-white mb-4">
                                Schedule a Consultation
                            </h2>
                            <p className="text-slate-400">
                                We'll discuss your portfolio structure and demonstrate how the platform 
                                addresses your specific oversight requirements.
                            </p>
                        </div>
                        
                        <form onSubmit={handleBetaSubmit} className="bg-slate-900/50 border border-slate-800 rounded-xl p-8">
                            <div className="space-y-5">
                                <div>
                                    <Label htmlFor="firmName" className="text-slate-400 text-sm">Firm Name *</Label>
                                    <Input
                                        id="firmName"
                                        value={betaForm.firmName}
                                        onChange={(e) => setBetaForm({...betaForm, firmName: e.target.value})}
                                        placeholder="Your accounting firm"
                                        className="mt-1.5 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-600"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="contactPerson" className="text-slate-400 text-sm">Contact Person</Label>
                                    <Input
                                        id="contactPerson"
                                        value={betaForm.contactPerson}
                                        onChange={(e) => setBetaForm({...betaForm, contactPerson: e.target.value})}
                                        placeholder="Your name"
                                        className="mt-1.5 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-600"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="email" className="text-slate-400 text-sm">Work Email *</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        value={betaForm.email}
                                        onChange={(e) => setBetaForm({...betaForm, email: e.target.value})}
                                        placeholder="you@yourfirm.dk"
                                        className="mt-1.5 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-600"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="activeClients" className="text-slate-400 text-sm">Number of Clients Managed</Label>
                                    <Input
                                        id="activeClients"
                                        value={betaForm.activeClients}
                                        onChange={(e) => setBetaForm({...betaForm, activeClients: e.target.value})}
                                        placeholder="e.g., 100-200"
                                        className="mt-1.5 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-600"
                                    />
                                </div>
                                <Button 
                                    type="submit" 
                                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white"
                                    disabled={submitting}
                                >
                                    {submitting ? 'Submitting...' : 'Request Consultation'}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-950 border-t border-slate-800/50 py-12">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8">
                        <div className="md:col-span-2">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center">
                                    <Shield className="w-5 h-5 text-emerald-500" />
                                </div>
                                <span className="font-medium text-white text-lg">Accountrix</span>
                            </div>
                            <p className="text-slate-500 text-sm leading-relaxed max-w-sm">
                                Professional control and risk intelligence for accounting firms 
                                managing large client portfolios.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-medium text-white text-sm mb-4">Platform</h4>
                            <ul className="space-y-2 text-sm text-slate-500">
                                <li><a href="#capabilities" className="hover:text-white transition-colors">Risk Dashboard</a></li>
                                <li><a href="#capabilities" className="hover:text-white transition-colors">Exception Inbox</a></li>
                                <li><a href="#capabilities" className="hover:text-white transition-colors">Pre-VAT Review</a></li>
                                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-medium text-white text-sm mb-4">Legal</h4>
                            <ul className="space-y-2 text-sm text-slate-500">
                                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">GDPR Compliance</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-slate-800/50 mt-10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-slate-600">
                            © 2026 Accountrix. All rights reserved.
                        </p>
                        <a href="mailto:contact@accountrix.dk" className="text-sm text-slate-500 hover:text-white transition-colors">
                            contact@accountrix.dk
                        </a>
                    </div>
                </div>
            </footer>
        </div>
    );
}
