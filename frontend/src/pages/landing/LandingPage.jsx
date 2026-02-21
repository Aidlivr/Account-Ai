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
    UserCheck
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
            <nav className="border-b border-slate-800 bg-slate-950/90 backdrop-blur-sm sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-white" />
                            </div>
                            <span className="font-semibold text-white text-lg tracking-tight">Accountrix</span>
                        </div>
                        <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
                            <a href="#problem" className="hover:text-white transition-colors">The Problem</a>
                            <a href="#platform" className="hover:text-white transition-colors">Platform</a>
                            <a href="#modules" className="hover:text-white transition-colors">Modules</a>
                            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
                        </div>
                        <div className="flex items-center gap-3">
                            <Link to="/login">
                                <Button variant="ghost" className="text-slate-400 hover:text-white hover:bg-slate-800">
                                    Sign In
                                </Button>
                            </Link>
                            <a href="#demo">
                                <Button className="bg-emerald-600 hover:bg-emerald-500 text-white">
                                    Request Demo
                                </Button>
                            </a>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-emerald-950/20 to-transparent"></div>
                <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32 relative">
                    <div className="max-w-3xl">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-sm mb-6">
                            <Eye className="w-4 h-4" />
                            Portfolio Risk Intelligence
                        </div>
                        <h1 className="text-4xl lg:text-5xl xl:text-6xl font-semibold text-white leading-tight mb-6">
                            Air Traffic Control for 
                            <span className="text-emerald-400"> Accounting Firms</span>
                        </h1>
                        <p className="text-xl text-slate-400 mb-8 leading-relaxed max-w-2xl">
                            Stop drowning in transaction noise. See which of your 100+ clients need attention before VAT deadlines. Catch anomalies before they become problems.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 mb-12">
                            <a href="#demo">
                                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-500 text-white px-8">
                                    Request Early Access
                                    <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            </a>
                            <a href="#platform">
                                <Button size="lg" variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white px-8">
                                    See How It Works
                                </Button>
                            </a>
                        </div>
                        
                        {/* Key Stats */}
                        <div className="grid grid-cols-3 gap-8 pt-8 border-t border-slate-800">
                            <div>
                                <div className="text-3xl font-semibold text-white">100+</div>
                                <div className="text-sm text-slate-500">Clients per firm</div>
                            </div>
                            <div>
                                <div className="text-3xl font-semibold text-white">80%</div>
                                <div className="text-sm text-slate-500">Review time reduction</div>
                            </div>
                            <div>
                                <div className="text-3xl font-semibold text-white">Pre-VAT</div>
                                <div className="text-sm text-slate-500">Risk detection</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Hero Visual - Control Dashboard Preview */}
                <div className="absolute right-0 top-32 w-1/2 hidden xl:block">
                    <div className="bg-slate-900 rounded-l-2xl border border-slate-800 p-6 shadow-2xl">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-sm font-medium text-slate-300">Portfolio Risk Overview</span>
                            <span className="text-xs text-slate-500">Live</span>
                        </div>
                        <div className="space-y-3">
                            {[
                                { client: 'Nordisk Handel ApS', risk: 'high', flags: 3, vat: '12 days' },
                                { client: 'TechStart Denmark', risk: 'medium', flags: 1, vat: '12 days' },
                                { client: 'Café Strøget IVS', risk: 'low', flags: 0, vat: '12 days' },
                                { client: 'Maritime Solutions', risk: 'high', flags: 5, vat: '12 days' },
                                { client: 'Green Energy DK', risk: 'low', flags: 0, vat: '12 days' },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-4 py-3">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${
                                            item.risk === 'high' ? 'bg-red-500' : 
                                            item.risk === 'medium' ? 'bg-amber-500' : 'bg-emerald-500'
                                        }`}></div>
                                        <span className="text-sm text-slate-300">{item.client}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        {item.flags > 0 && (
                                            <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-400">
                                                {item.flags} flags
                                            </span>
                                        )}
                                        <span className="text-xs text-slate-500">VAT: {item.vat}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* The Problem Section */}
            <section id="problem" className="py-24 bg-slate-900/50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-16">
                        <h2 className="text-3xl font-semibold text-white mb-4">
                            Managing 100+ Clients Creates Cognitive Overload
                        </h2>
                        <p className="text-slate-400">
                            Your accounting system shows you everything. But when you're responsible for hundreds of clients, you need to see what matters.
                        </p>
                    </div>
                    
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            {
                                icon: AlertTriangle,
                                title: 'Which clients need attention?',
                                description: 'With 100+ clients, you cannot review every transaction. You need to know which clients have anomalies before VAT submission.'
                            },
                            {
                                icon: TrendingUp,
                                title: 'Where are the unusual patterns?',
                                description: 'A sudden spike in expenses or an unusual VAT percentage could indicate errors—or fraud. Manual detection is impossible at scale.'
                            },
                            {
                                icon: Clock,
                                title: 'VAT deadlines create pressure',
                                description: 'Before every VAT period, you review frantically. But without prioritization, you waste time on low-risk clients.'
                            },
                            {
                                icon: Users,
                                title: 'Junior staff need oversight',
                                description: 'Your team posts thousands of entries. How do you know which ones need senior review without checking everything?'
                            },
                            {
                                icon: FileSearch,
                                title: 'Compliance risks hide in volume',
                                description: 'Duplicate invoices, suspicious vendors, and coding errors get buried in transaction volume. Problems surface too late.'
                            },
                            {
                                icon: Layers,
                                title: 'Systems show data, not insight',
                                description: 'e-conomic shows you what happened. It doesn\'t tell you what\'s wrong, what\'s unusual, or what needs your attention.'
                            }
                        ].map((item, i) => (
                            <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
                                <item.icon className="w-8 h-8 text-red-400 mb-4" />
                                <h3 className="font-medium text-white mb-2">{item.title}</h3>
                                <p className="text-sm text-slate-400 leading-relaxed">{item.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Platform Positioning */}
            <section id="platform" className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        <div>
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full text-slate-400 text-sm mb-6">
                                <Layers className="w-4 h-4" />
                                Control Layer Architecture
                            </div>
                            <h2 className="text-3xl font-semibold text-white mb-6">
                                We Sit Above Your Accounting System
                            </h2>
                            <p className="text-slate-400 mb-8 leading-relaxed">
                                Accountrix doesn't replace e-conomic or compete with built-in features. We connect to your existing systems and provide the intelligence layer that's missing: cross-client risk visibility, exception detection, and pre-VAT control.
                            </p>
                            <div className="space-y-4">
                                {[
                                    { label: 'Not an OCR tool', desc: 'We don\'t process invoices. We analyze patterns.' },
                                    { label: 'Not automation', desc: 'We provide oversight, not replacement.' },
                                    { label: 'Not per-client', desc: 'Portfolio-wide intelligence across all your clients.' },
                                ].map((item, i) => (
                                    <div key={i} className="flex items-start gap-3">
                                        <CheckCircle className="w-5 h-5 text-emerald-500 mt-0.5" />
                                        <div>
                                            <span className="text-white font-medium">{item.label}</span>
                                            <span className="text-slate-500"> — {item.desc}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        {/* Architecture Diagram */}
                        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8">
                            <div className="space-y-4">
                                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-center">
                                    <Shield className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
                                    <div className="text-emerald-400 font-medium">Accountrix</div>
                                    <div className="text-xs text-emerald-400/70">Risk & Control Intelligence</div>
                                </div>
                                <div className="flex justify-center">
                                    <div className="w-px h-8 bg-slate-700"></div>
                                </div>
                                <div className="text-center text-xs text-slate-500 py-2">
                                    API Connection
                                </div>
                                <div className="flex justify-center">
                                    <div className="w-px h-8 bg-slate-700"></div>
                                </div>
                                <div className="grid grid-cols-3 gap-3">
                                    {['e-conomic', 'Dinero', 'Fortnox'].map((sys, i) => (
                                        <div key={i} className="bg-slate-800 rounded-lg p-3 text-center">
                                            <Building2 className="w-5 h-5 text-slate-500 mx-auto mb-1" />
                                            <div className="text-xs text-slate-400">{sys}</div>
                                        </div>
                                    ))}
                                </div>
                                <div className="text-center text-xs text-slate-600 mt-4">
                                    Your existing accounting systems
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Modules */}
            <section id="modules" className="py-24 bg-slate-900/50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-semibold text-white mb-4">
                            Three Modules. Complete Control.
                        </h2>
                        <p className="text-slate-400 max-w-2xl mx-auto">
                            Built for partners and senior reviewers who need to maintain oversight across large client portfolios.
                        </p>
                    </div>
                    
                    <div className="grid lg:grid-cols-3 gap-8">
                        {/* Module 1 */}
                        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
                            <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center mb-6">
                                <Target className="w-6 h-6 text-red-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-3">Portfolio Risk Dashboard</h3>
                            <p className="text-slate-400 text-sm mb-6">
                                See all your clients ranked by risk. Traffic-light indicators show who needs attention now.
                            </p>
                            <ul className="space-y-3">
                                {[
                                    'Risk score per client',
                                    'VAT trend anomalies',
                                    'Expense spike detection',
                                    'Duplicate invoice alerts',
                                    'Missing documentation flags'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                                        <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        {/* Module 2 */}
                        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
                            <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center mb-6">
                                <Bell className="w-6 h-6 text-amber-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-3">Exception Inbox</h3>
                            <p className="text-slate-400 text-sm mb-6">
                                Only see what matters. Flagged transactions with explanations and quick actions.
                            </p>
                            <ul className="space-y-3">
                                {[
                                    'Unusual transaction detection',
                                    'Pattern deviation alerts',
                                    'High VAT impact entries',
                                    'Suspicious vendor patterns',
                                    'One-click review actions'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                                        <div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        {/* Module 3 */}
                        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
                            <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6">
                                <Clock className="w-6 h-6 text-emerald-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-3">Pre-VAT Control Mode</h3>
                            <p className="text-slate-400 text-sm mb-6">
                                As VAT deadline approaches, automatic risk summary per client. Never miss a problem.
                            </p>
                            <ul className="space-y-3">
                                {[
                                    'VAT percentage changes',
                                    'Quarter vs history comparison',
                                    'Unusual deduction patterns',
                                    'Missing VAT-coded entries',
                                    'Pre-submission checklist'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                                        <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></div>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-semibold text-white mb-4">
                            From Data Overload to Clear Priorities
                        </h2>
                    </div>
                    
                    <div className="grid md:grid-cols-4 gap-6">
                        {[
                            { step: '1', title: 'Connect', desc: 'Link your e-conomic accounts via secure API', icon: Zap },
                            { step: '2', title: 'Analyze', desc: 'AI builds baseline patterns per client', icon: BarChart3 },
                            { step: '3', title: 'Detect', desc: 'Anomalies surface automatically', icon: AlertTriangle },
                            { step: '4', title: 'Control', desc: 'Review, approve, or investigate', icon: UserCheck },
                        ].map((item, i) => (
                            <div key={i} className="text-center">
                                <div className="w-14 h-14 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-slate-700">
                                    <item.icon className="w-6 h-6 text-emerald-400" />
                                </div>
                                <div className="text-emerald-400 text-sm font-medium mb-2">Step {item.step}</div>
                                <h4 className="text-white font-medium mb-2">{item.title}</h4>
                                <p className="text-sm text-slate-500">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Audit Trail / Trust Section */}
            <section className="py-24 bg-slate-900/50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-8">
                            <div className="text-sm text-slate-500 mb-4">Exception Detail</div>
                            <div className="bg-slate-900 rounded-xl p-6 mb-4">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <div className="text-white font-medium">Unusual expense detected</div>
                                        <div className="text-slate-500 text-sm">Nordisk Handel ApS</div>
                                    </div>
                                    <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">High Priority</span>
                                </div>
                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Transaction</span>
                                        <span className="text-slate-300">Office Equipment - 47,500 DKK</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Historical average</span>
                                        <span className="text-slate-300">3,200 DKK/month</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Deviation</span>
                                        <span className="text-red-400">+1,384%</span>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                                <div className="text-xs text-slate-500 mb-2">AI Explanation</div>
                                <p className="text-sm text-slate-400">
                                    "This expense is 14x higher than the 12-month average for account 6310 (IT Equipment). 
                                    Similar spikes in past were approved as capital purchases. Recommend verification of asset classification."
                                </p>
                            </div>
                            <div className="flex gap-3 mt-6">
                                <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500">Approve</Button>
                                <Button size="sm" variant="outline" className="border-slate-600 text-slate-300">Investigate</Button>
                                <Button size="sm" variant="outline" className="border-slate-600 text-slate-300">Assign</Button>
                            </div>
                        </div>
                        
                        <div>
                            <h2 className="text-3xl font-semibold text-white mb-6">
                                No Black Box Decisions
                            </h2>
                            <p className="text-slate-400 mb-8 leading-relaxed">
                                Every flag includes a clear explanation. See why something was flagged, what the historical comparison shows, and what action is recommended. You decide—the system advises.
                            </p>
                            <div className="space-y-4">
                                {[
                                    { icon: Eye, text: 'Full transparency on every flag' },
                                    { icon: BarChart3, text: 'Historical data comparison included' },
                                    { icon: FileSearch, text: 'Complete audit trail' },
                                    { icon: UserCheck, text: 'Human approval required for all actions' },
                                ].map((item, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center">
                                            <item.icon className="w-4 h-4 text-emerald-400" />
                                        </div>
                                        <span className="text-slate-300">{item.text}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-24">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-semibold text-white mb-4">
                            Pricing Built for Firms, Not Invoices
                        </h2>
                        <p className="text-slate-400">
                            Simple per-firm pricing. Scales with your client portfolio.
                        </p>
                    </div>
                    
                    <div className="max-w-lg mx-auto">
                        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden">
                            <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 px-8 py-6">
                                <h3 className="text-white font-semibold text-xl">Professional</h3>
                                <p className="text-emerald-100 text-sm">For accounting firms managing 50-300 clients</p>
                            </div>
                            <div className="p-8">
                                <div className="text-center mb-8">
                                    <div className="text-slate-500 text-sm mb-2">Starting from</div>
                                    <div className="flex items-baseline justify-center gap-1">
                                        <span className="text-4xl font-semibold text-white">2.499</span>
                                        <span className="text-slate-400">DKK / month</span>
                                    </div>
                                    <p className="text-slate-500 text-sm mt-2">
                                        Includes up to 100 connected clients
                                    </p>
                                </div>
                                
                                <div className="bg-slate-900/50 rounded-xl p-4 mb-8">
                                    <div className="text-center">
                                        <span className="text-slate-400 text-sm">Additional clients:</span>
                                        <span className="text-white font-medium ml-2">+15 DKK/client/month</span>
                                    </div>
                                </div>
                                
                                <ul className="space-y-3 mb-8">
                                    {[
                                        'Portfolio Risk Dashboard',
                                        'Exception Inbox',
                                        'Pre-VAT Control Mode',
                                        'Unlimited users',
                                        'e-conomic integration',
                                        'Transaction Intelligence',
                                        'Email support'
                                    ].map((item, i) => (
                                        <li key={i} className="flex items-center gap-3 text-slate-300">
                                            <CheckCircle className="w-4 h-4 text-emerald-500" />
                                            <span className="text-sm">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                
                                <a href="#demo" className="block">
                                    <Button className="w-full bg-emerald-600 hover:bg-emerald-500 text-white">
                                        Request Demo
                                    </Button>
                                </a>
                            </div>
                        </div>
                        
                        <p className="text-center text-sm text-slate-500 mt-6">
                            Not per-invoice. Not per-transaction. Simple firm-level pricing.
                        </p>
                    </div>
                </div>
            </section>

            {/* Demo Request Section */}
            <section id="demo" className="py-24 bg-slate-900/50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-2xl mx-auto">
                        <div className="text-center mb-10">
                            <h2 className="text-3xl font-semibold text-white mb-4">
                                See Accountrix in Action
                            </h2>
                            <p className="text-slate-400">
                                Request a demo tailored to your firm's portfolio. We'll show you exactly which of your clients would benefit most.
                            </p>
                        </div>
                        
                        <form onSubmit={handleBetaSubmit} className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
                            <div className="space-y-5">
                                <div>
                                    <Label htmlFor="firmName" className="text-slate-300">Firm Name *</Label>
                                    <Input
                                        id="firmName"
                                        value={betaForm.firmName}
                                        onChange={(e) => setBetaForm({...betaForm, firmName: e.target.value})}
                                        placeholder="Your accounting firm"
                                        className="mt-1.5 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="contactPerson" className="text-slate-300">Contact Person</Label>
                                    <Input
                                        id="contactPerson"
                                        value={betaForm.contactPerson}
                                        onChange={(e) => setBetaForm({...betaForm, contactPerson: e.target.value})}
                                        placeholder="Your name"
                                        className="mt-1.5 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="email" className="text-slate-300">Work Email *</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        value={betaForm.email}
                                        onChange={(e) => setBetaForm({...betaForm, email: e.target.value})}
                                        placeholder="you@yourfirm.dk"
                                        className="mt-1.5 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="activeClients" className="text-slate-300">Number of Clients You Manage</Label>
                                    <Input
                                        id="activeClients"
                                        value={betaForm.activeClients}
                                        onChange={(e) => setBetaForm({...betaForm, activeClients: e.target.value})}
                                        placeholder="e.g., 100-200"
                                        className="mt-1.5 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                                    />
                                </div>
                                <Button 
                                    type="submit" 
                                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white"
                                    disabled={submitting}
                                >
                                    {submitting ? 'Submitting...' : 'Request Demo'}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-950 border-t border-slate-800 py-12">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8">
                        <div className="md:col-span-2">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                                    <Shield className="w-5 h-5 text-white" />
                                </div>
                                <span className="font-semibold text-white text-lg">Accountrix</span>
                            </div>
                            <p className="text-slate-500 text-sm leading-relaxed max-w-md">
                                Portfolio Risk & Control Intelligence for accounting firms. 
                                Built for partners managing 100+ clients who need clarity, not more data.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-medium text-white mb-4">Platform</h4>
                            <ul className="space-y-2 text-sm text-slate-500">
                                <li><a href="#modules" className="hover:text-white transition-colors">Risk Dashboard</a></li>
                                <li><a href="#modules" className="hover:text-white transition-colors">Exception Inbox</a></li>
                                <li><a href="#modules" className="hover:text-white transition-colors">Pre-VAT Control</a></li>
                                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-medium text-white mb-4">Legal</h4>
                            <ul className="space-y-2 text-sm text-slate-500">
                                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">GDPR Compliance</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-slate-800 mt-10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-slate-600">
                            © 2026 Accountrix. All rights reserved.
                        </p>
                        <div className="flex items-center gap-6">
                            <a href="mailto:hello@accountrix.dk" className="text-sm text-slate-500 hover:text-white transition-colors">
                                hello@accountrix.dk
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
