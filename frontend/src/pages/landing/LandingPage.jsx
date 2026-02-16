import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
    FileText, 
    CheckCircle, 
    Shield, 
    BarChart3, 
    Users, 
    Clock,
    ArrowRight,
    Building2,
    Settings,
    Lock,
    Activity,
    ChevronRight
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';

// Beta request form submission
const submitBetaRequest = async (formData) => {
    // In production, this would submit to backend
    console.log('Beta request:', formData);
    return { success: true };
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
            await submitBetaRequest(betaForm);
            toast.success('Thank you for your interest. We will contact you shortly.');
            setBetaForm({ firmName: '', contactPerson: '', email: '', activeClients: '' });
        } catch (err) {
            toast.error('Submission failed. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="border-b border-slate-200 bg-white sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-[#1e3a5f] rounded flex items-center justify-center">
                                <FileText className="w-4 h-4 text-white" />
                            </div>
                            <span className="font-semibold text-[#1e3a5f] text-lg">Accountrix</span>
                        </div>
                        <div className="hidden md:flex items-center gap-8 text-sm text-slate-600">
                            <a href="#features" className="hover:text-[#1e3a5f] transition-colors">Features</a>
                            <a href="#workflow" className="hover:text-[#1e3a5f] transition-colors">How It Works</a>
                            <a href="#pricing" className="hover:text-[#1e3a5f] transition-colors">Pricing</a>
                            <a href="#security" className="hover:text-[#1e3a5f] transition-colors">Security</a>
                        </div>
                        <div className="flex items-center gap-3">
                            <Link to="/login">
                                <Button variant="ghost" className="text-slate-600 hover:text-[#1e3a5f]">
                                    Sign In
                                </Button>
                            </Link>
                            <a href="#beta">
                                <Button className="bg-[#1e3a5f] hover:bg-[#2d4a6f] text-white">
                                    Request Access
                                </Button>
                            </a>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="bg-gradient-to-b from-slate-50 to-white py-20 lg:py-28">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h1 className="text-4xl lg:text-5xl font-semibold text-[#1e3a5f] leading-tight mb-6">
                                AI Accounting Copilot for Modern Accounting Firms
                            </h1>
                            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                                Reduce manual bookkeeping workload with structured AI-powered invoice processing — fully reviewable and compliant with e-conomic.
                            </p>
                            <ul className="space-y-3 mb-8">
                                {[
                                    'AI invoice extraction with rule-based validation',
                                    'Accountant-controlled approval workflow',
                                    'Draft voucher creation in e-conomic',
                                    'Built for Danish VAT compliance'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-slate-700">
                                        <CheckCircle className="w-5 h-5 text-[#1e3a5f] mt-0.5 flex-shrink-0" />
                                        <span>{item}</span>
                                    </li>
                                ))}
                            </ul>
                            <div className="flex flex-col sm:flex-row gap-4">
                                <a href="#beta">
                                    <Button size="lg" className="bg-[#1e3a5f] hover:bg-[#2d4a6f] text-white px-8">
                                        Request Early Access
                                        <ArrowRight className="w-4 h-4 ml-2" />
                                    </Button>
                                </a>
                                <a href="#workflow">
                                    <Button size="lg" variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 px-8">
                                        Book a Demo
                                    </Button>
                                </a>
                            </div>
                        </div>
                        <div className="bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden">
                            <div className="bg-[#1e3a5f] px-4 py-3 flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-slate-400"></div>
                                <div className="w-3 h-3 rounded-full bg-slate-400"></div>
                                <div className="w-3 h-3 rounded-full bg-slate-400"></div>
                                <span className="text-white/80 text-sm ml-2">Invoice Review Queue</span>
                            </div>
                            <div className="p-6">
                                {/* Mock Dashboard */}
                                <div className="space-y-4">
                                    {[
                                        { vendor: 'Lyreco Denmark A/S', amount: '2.176,25', confidence: 98, account: '6300' },
                                        { vendor: 'TDC Erhverv', amount: '2.164,38', confidence: 95, account: '6400' },
                                        { vendor: 'Dustin A/S', amount: '38.671,25', confidence: 92, account: '6310' },
                                    ].map((item, i) => (
                                        <div key={i} className="border border-slate-200 rounded-lg p-4 hover:border-[#1e3a5f]/30 transition-colors">
                                            <div className="flex items-center justify-between mb-3">
                                                <div>
                                                    <p className="font-medium text-slate-800">{item.vendor}</p>
                                                    <p className="text-sm text-slate-500">Invoice pending review</p>
                                                </div>
                                                <span className="text-lg font-semibold text-slate-800">{item.amount} DKK</span>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-4 text-sm">
                                                    <span className="flex items-center gap-1.5">
                                                        <div className={`w-2 h-2 rounded-full ${item.confidence >= 95 ? 'bg-green-500' : 'bg-amber-500'}`}></div>
                                                        <span className="text-slate-600">{item.confidence}% confidence</span>
                                                    </span>
                                                    <span className="text-slate-400">|</span>
                                                    <span className="text-slate-600">Account: {item.account}</span>
                                                </div>
                                                <Button size="sm" className="bg-[#1e3a5f] hover:bg-[#2d4a6f] text-white text-xs h-8">
                                                    Approve
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* The Problem Section */}
            <section className="py-20 bg-white">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-12">
                        <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                            Manual Invoice Processing Slows Down Accounting Firms
                        </h2>
                        <p className="text-slate-600">
                            Traditional invoice handling creates bottlenecks that affect your entire practice.
                        </p>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            {
                                title: 'Time-Intensive Data Entry',
                                description: 'Accountants spend hours manually posting invoices, extracting vendor details, amounts, and VAT information from each document.'
                            },
                            {
                                title: 'Repetitive Classification',
                                description: 'The same vendors require the same account classifications month after month, yet each invoice is processed individually.'
                            },
                            {
                                title: 'VAT Rule Verification',
                                description: 'Danish VAT rules require careful verification. Reverse charge, EU acquisitions, and exempt services each need specific handling.'
                            },
                            {
                                title: 'Peak Period Errors',
                                description: 'During busy periods like quarter-end, manual processing increases the risk of posting errors and classification mistakes.'
                            },
                            {
                                title: 'Client Expectations',
                                description: 'Clients expect faster financial reporting. Manual processes create delays that affect your service delivery.'
                            },
                            {
                                title: 'Scaling Challenges',
                                description: 'Growing your client base means proportionally more manual work, limiting the efficiency gains from economies of scale.'
                            }
                        ].map((item, i) => (
                            <div key={i} className="bg-slate-50 rounded-lg p-6 border border-slate-100">
                                <h3 className="font-medium text-[#1e3a5f] mb-2">{item.title}</h3>
                                <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* The Solution Section */}
            <section id="workflow" className="py-20 bg-slate-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-16">
                        <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                            A Structured AI Assistant — Not Uncontrolled Automation
                        </h2>
                        <p className="text-slate-600">
                            Our system provides intelligent suggestions while keeping accountants in full control of every posting decision.
                        </p>
                    </div>
                    
                    <div className="grid lg:grid-cols-6 gap-4">
                        {[
                            { step: '1', title: 'Upload', desc: 'PDF or image invoices', icon: FileText },
                            { step: '2', title: 'Extract', desc: 'AI structures the data', icon: Settings },
                            { step: '3', title: 'Validate', desc: 'Rule engine checks VAT', icon: Shield },
                            { step: '4', title: 'Review', desc: 'Accountant verifies', icon: Users },
                            { step: '5', title: 'Approve', desc: 'Bulk or individual', icon: CheckCircle },
                            { step: '6', title: 'Post', desc: 'Draft to e-conomic', icon: ArrowRight },
                        ].map((item, i) => (
                            <div key={i} className="relative">
                                <div className="bg-white rounded-lg p-5 border border-slate-200 text-center h-full">
                                    <div className="w-10 h-10 bg-[#1e3a5f] rounded-full flex items-center justify-center mx-auto mb-3">
                                        <item.icon className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="text-xs font-medium text-[#1e3a5f] mb-1">Step {item.step}</div>
                                    <h4 className="font-medium text-slate-800 mb-1">{item.title}</h4>
                                    <p className="text-xs text-slate-500">{item.desc}</p>
                                </div>
                                {i < 5 && (
                                    <div className="hidden lg:block absolute top-1/2 -right-2 transform -translate-y-1/2 z-10">
                                        <ChevronRight className="w-4 h-4 text-slate-300" />
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="mt-16 grid md:grid-cols-2 gap-8">
                        <div className="bg-white rounded-lg p-8 border border-slate-200">
                            <h3 className="font-semibold text-[#1e3a5f] mb-4">Accountant Control</h3>
                            <ul className="space-y-3">
                                {[
                                    'No automatic posting without explicit approval',
                                    'Full visibility of AI confidence scores',
                                    'Edit any extracted field before approval',
                                    'Reject invoices that require manual handling'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-slate-600">
                                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                                        <span className="text-sm">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-white rounded-lg p-8 border border-slate-200">
                            <h3 className="font-semibold text-[#1e3a5f] mb-4">Continuous Improvement</h3>
                            <ul className="space-y-3">
                                {[
                                    'Vendor learning adapts to your corrections',
                                    'Account suggestions improve over time',
                                    'Company-specific rules respected',
                                    'Accuracy metrics tracked per client'
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-slate-600">
                                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                                        <span className="text-sm">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* Key Features Section */}
            <section id="features" className="py-20 bg-white">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-16">
                        <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                            Built for Professional Accounting Workflows
                        </h2>
                        <p className="text-slate-600">
                            Every feature designed with input from practicing accountants.
                        </p>
                    </div>
                    
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[
                            {
                                icon: FileText,
                                title: 'Intelligent Invoice Extraction',
                                description: 'Structured JSON output with vendor name, CVR, amounts, dates, and line items. High accuracy on critical fields.'
                            },
                            {
                                icon: Settings,
                                title: 'Deterministic Rule Engine',
                                description: 'Built-in Danish VAT logic including standard 25%, reverse charge, EU acquisitions, and exempt categories.'
                            },
                            {
                                icon: Users,
                                title: 'Vendor Learning System',
                                description: 'System learns from your corrections. After consistent approvals, account suggestions match your preferences.'
                            },
                            {
                                icon: CheckCircle,
                                title: 'Bulk Approval Workflow',
                                description: 'Review and approve multiple invoices efficiently. Filter by confidence level, vendor, or amount.'
                            },
                            {
                                icon: Building2,
                                title: 'e-conomic Integration',
                                description: 'Draft voucher creation via secure OAuth connection. Review in Accountrix, post to e-conomic.'
                            },
                            {
                                icon: BarChart3,
                                title: 'Accuracy Dashboard',
                                description: 'Track AI accuracy per client, identify vendors needing attention, and measure time saved.'
                            }
                        ].map((feature, i) => (
                            <div key={i} className="bg-slate-50 rounded-lg p-6 border border-slate-100 hover:border-[#1e3a5f]/20 transition-colors">
                                <div className="w-12 h-12 bg-[#1e3a5f]/10 rounded-lg flex items-center justify-center mb-4">
                                    <feature.icon className="w-6 h-6 text-[#1e3a5f]" />
                                </div>
                                <h3 className="font-semibold text-[#1e3a5f] mb-2">{feature.title}</h3>
                                <p className="text-sm text-slate-600 leading-relaxed">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Validation Results Section */}
            <section className="py-16 bg-slate-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-10">
                        <h2 className="text-2xl font-semibold text-[#1e3a5f] mb-2">Internal Validation Results</h2>
                        <p className="text-sm text-slate-500">Based on 50-invoice test suite with Danish vendor patterns</p>
                    </div>
                    <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
                        {[
                            { value: '88%', label: 'Account Classification Accuracy' },
                            { value: '100%', label: 'Amount Extraction Accuracy' },
                            { value: '2.17%', label: 'Error Rate' },
                        ].map((stat, i) => (
                            <div key={i} className="bg-white rounded-lg p-6 border border-slate-200 text-center">
                                <div className="text-3xl font-semibold text-[#1e3a5f] mb-1">{stat.value}</div>
                                <div className="text-sm text-slate-600">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Security Section */}
            <section id="security" className="py-20 bg-white">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                                Built with European Compliance in Mind
                            </h2>
                            <p className="text-slate-600 mb-8">
                                We understand that accounting firms handle sensitive financial data. Our architecture reflects that responsibility.
                            </p>
                            <ul className="space-y-4">
                                {[
                                    { icon: CheckCircle, text: 'Accountant review required before any posting' },
                                    { icon: Lock, text: 'Secure OAuth token-based authentication' },
                                    { icon: Shield, text: 'Encrypted data storage and transmission' },
                                    { icon: Building2, text: 'Multi-tenant architecture with data isolation' },
                                    { icon: Activity, text: 'Complete activity logs for audit trails' },
                                    { icon: FileText, text: 'Designed for Danish bookkeeping standards' },
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3">
                                        <div className="w-8 h-8 bg-[#1e3a5f]/10 rounded flex items-center justify-center flex-shrink-0">
                                            <item.icon className="w-4 h-4 text-[#1e3a5f]" />
                                        </div>
                                        <span className="text-slate-700 pt-1">{item.text}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-slate-50 rounded-lg p-8 border border-slate-200">
                            <div className="text-center">
                                <Lock className="w-16 h-16 text-[#1e3a5f] mx-auto mb-6" />
                                <h3 className="font-semibold text-[#1e3a5f] mb-4">Data Security Principles</h3>
                                <div className="space-y-4 text-left">
                                    <div className="bg-white rounded p-4 border border-slate-100">
                                        <h4 className="font-medium text-slate-800 text-sm mb-1">No Automatic Posting</h4>
                                        <p className="text-xs text-slate-500">Every voucher requires explicit accountant approval before reaching e-conomic.</p>
                                    </div>
                                    <div className="bg-white rounded p-4 border border-slate-100">
                                        <h4 className="font-medium text-slate-800 text-sm mb-1">Client Data Isolation</h4>
                                        <p className="text-xs text-slate-500">Each client company's data is logically separated with strict access controls.</p>
                                    </div>
                                    <div className="bg-white rounded p-4 border border-slate-100">
                                        <h4 className="font-medium text-slate-800 text-sm mb-1">Audit Trail</h4>
                                        <p className="text-xs text-slate-500">Every action is logged with timestamp, user, and change details.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-20 bg-slate-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-3xl mx-auto text-center mb-12">
                        <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                            Simple Pricing for Accounting Firms
                        </h2>
                        <p className="text-slate-600">
                            Pay a base subscription plus a per-client fee. Only active companies count.
                        </p>
                    </div>
                    
                    <div className="max-w-lg mx-auto">
                        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                            <div className="bg-[#1e3a5f] px-8 py-6 text-center">
                                <h3 className="text-white font-semibold text-xl mb-1">Accountrix Professional</h3>
                                <p className="text-white/70 text-sm">For accounting firms of all sizes</p>
                            </div>
                            <div className="p-8">
                                <div className="text-center mb-8">
                                    <div className="flex items-baseline justify-center gap-1 mb-2">
                                        <span className="text-4xl font-semibold text-[#1e3a5f]">399</span>
                                        <span className="text-slate-600">DKK / month</span>
                                    </div>
                                    <p className="text-slate-500 text-sm">Base subscription</p>
                                </div>
                                
                                <div className="bg-slate-50 rounded-lg p-4 mb-8 text-center">
                                    <div className="flex items-baseline justify-center gap-1 mb-1">
                                        <span className="text-2xl font-semibold text-[#1e3a5f]">+ 69</span>
                                        <span className="text-slate-600">DKK</span>
                                    </div>
                                    <p className="text-sm text-slate-500">per active company / month</p>
                                </div>
                                
                                <ul className="space-y-3 mb-8">
                                    {[
                                        'Unlimited users',
                                        'AI invoice extraction',
                                        'Vendor learning system',
                                        'e-conomic integration',
                                        'Accuracy dashboard',
                                        'Email support'
                                    ].map((item, i) => (
                                        <li key={i} className="flex items-center gap-3 text-slate-600">
                                            <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                                            <span className="text-sm">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                                
                                <a href="#beta" className="block">
                                    <Button className="w-full bg-[#1e3a5f] hover:bg-[#2d4a6f] text-white">
                                        Join Beta Program
                                    </Button>
                                </a>
                            </div>
                        </div>
                        
                        <p className="text-center text-sm text-slate-500 mt-6">
                            Only companies with processed invoices during the billing period are counted as active.
                        </p>
                    </div>
                </div>
            </section>

            {/* Beta Invitation Section */}
            <section id="beta" className="py-20 bg-white">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="max-w-2xl mx-auto">
                        <div className="text-center mb-10">
                            <h2 className="text-3xl font-semibold text-[#1e3a5f] mb-4">
                                Currently Available for Selected Accounting Firms
                            </h2>
                            <p className="text-slate-600">
                                We are onboarding a limited number of firms for early access to ensure quality support during the beta period.
                            </p>
                        </div>
                        
                        <form onSubmit={handleBetaSubmit} className="bg-slate-50 rounded-lg p-8 border border-slate-200">
                            <div className="space-y-5">
                                <div>
                                    <Label htmlFor="firmName" className="text-slate-700">Firm Name *</Label>
                                    <Input
                                        id="firmName"
                                        value={betaForm.firmName}
                                        onChange={(e) => setBetaForm({...betaForm, firmName: e.target.value})}
                                        placeholder="Your accounting firm"
                                        className="mt-1.5 bg-white"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="contactPerson" className="text-slate-700">Contact Person</Label>
                                    <Input
                                        id="contactPerson"
                                        value={betaForm.contactPerson}
                                        onChange={(e) => setBetaForm({...betaForm, contactPerson: e.target.value})}
                                        placeholder="Your name"
                                        className="mt-1.5 bg-white"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="email" className="text-slate-700">Email *</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        value={betaForm.email}
                                        onChange={(e) => setBetaForm({...betaForm, email: e.target.value})}
                                        placeholder="email@yourfirm.dk"
                                        className="mt-1.5 bg-white"
                                        required
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="activeClients" className="text-slate-700">Number of Active Clients</Label>
                                    <Input
                                        id="activeClients"
                                        value={betaForm.activeClients}
                                        onChange={(e) => setBetaForm({...betaForm, activeClients: e.target.value})}
                                        placeholder="e.g., 25-50"
                                        className="mt-1.5 bg-white"
                                    />
                                </div>
                                <Button 
                                    type="submit" 
                                    className="w-full bg-[#1e3a5f] hover:bg-[#2d4a6f] text-white"
                                    disabled={submitting}
                                >
                                    {submitting ? 'Submitting...' : 'Request Early Access'}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-[#1e3a5f] text-white py-12">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8">
                        <div className="md:col-span-2">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-8 h-8 bg-white/10 rounded flex items-center justify-center">
                                    <FileText className="w-4 h-4 text-white" />
                                </div>
                                <span className="font-semibold text-lg">Accountrix</span>
                            </div>
                            <p className="text-white/70 text-sm leading-relaxed max-w-md">
                                AI-assisted invoice processing for Danish accounting firms. Built for e-conomic integration with accountant-controlled workflows.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-medium mb-4">Product</h4>
                            <ul className="space-y-2 text-sm text-white/70">
                                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                                <li><a href="#workflow" className="hover:text-white transition-colors">How It Works</a></li>
                                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                                <li><a href="#security" className="hover:text-white transition-colors">Security</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-medium mb-4">Legal</h4>
                            <ul className="space-y-2 text-sm text-white/70">
                                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Cookie Policy</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-white/10 mt-10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-white/50">
                            Accountrix ApS. All rights reserved.
                        </p>
                        <div className="flex items-center gap-6">
                            <a href="mailto:contact@accountrix.dk" className="text-sm text-white/70 hover:text-white transition-colors">
                                contact@accountrix.dk
                            </a>
                            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="text-white/70 hover:text-white transition-colors">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
