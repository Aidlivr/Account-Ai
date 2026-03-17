import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { CheckCircle, Building, Shield, ArrowRight, ExternalLink, RefreshCw, BarChart3, Bell, Clock } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const PUBLIC_TOKEN = 'XMTQAfaSihOXVVi6WUwEB3yLmvn3BqIecYosMABmvis';

const authHeaders = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

const steps = [
    { id: 1, title: 'Welcome', icon: Shield },
    { id: 2, title: 'Connect e-conomic', icon: Building },
    { id: 3, title: 'Sync clients', icon: RefreshCw },
    { id: 4, title: "You're ready!", icon: CheckCircle },
];

export default function OnboardingPage() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState(null);

    const connectEconomic = () => {
        const callbackUrl = encodeURIComponent(
            `${BACKEND_URL}/api/user/economic/callback?user_id=${user?.id}`
        );
        const url = `https://secure.e-conomic.com/secure/api1/requestaccess.aspx?appPublicToken=${PUBLIC_TOKEN}&redirectUrl=${callbackUrl}`;
        window.open(url, '_blank');
    };

    const syncClients = async () => {
        setSyncing(true);
        try {
            const res = await axios.post(`${BACKEND_URL}/api/user/economic/sync`, {}, authHeaders());
            setSyncResult(res.data);
            if (res.data.success) {
                toast.success(`${res.data.synced} clients synced!`);
                setCurrentStep(4);
            } else {
                toast.error(res.data.message || 'Sync failed');
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Sync failed — make sure you completed the e-conomic connection');
        } finally {
            setSyncing(false);
        }
    };

    const skipToDemo = () => {
        localStorage.setItem('onboarding_complete', 'true');
        navigate('/app/portfolio');
    };

    const goToDashboard = () => {
        localStorage.setItem('onboarding_complete', 'true');
        navigate('/app/portfolio');
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
            <div className="w-full max-w-2xl">

                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-2 mb-2">
                        <Shield className="h-8 w-8 text-teal-400" />
                        <span className="text-2xl font-bold text-white">Accountrix</span>
                    </div>
                    <p className="text-slate-400 text-sm">Professional Control Across Your Entire Client Portfolio</p>
                </div>

                {/* Step indicators */}
                <div className="flex items-center justify-center gap-2 mb-8">
                    {steps.map((step, idx) => (
                        <React.Fragment key={step.id}>
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                                currentStep === step.id
                                    ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
                                    : currentStep > step.id
                                    ? 'bg-green-500/10 text-green-400'
                                    : 'text-slate-600'
                            }`}>
                                {currentStep > step.id
                                    ? <CheckCircle className="h-3 w-3" />
                                    : <step.icon className="h-3 w-3" />}
                                <span className="hidden sm:inline">{step.title}</span>
                            </div>
                            {idx < steps.length - 1 && (
                                <div className={`h-px w-6 ${currentStep > step.id ? 'bg-green-500/40' : 'bg-slate-700'}`} />
                            )}
                        </React.Fragment>
                    ))}
                </div>

                {/* Step content */}
                <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-8">

                        {/* Step 1 — Welcome */}
                        {currentStep === 1 && (
                            <div className="text-center space-y-6">
                                <div className="w-16 h-16 bg-teal-500/10 rounded-full flex items-center justify-center mx-auto">
                                    <Shield className="h-8 w-8 text-teal-400" />
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-white mb-2">
                                        Welcome, {user?.name?.split(' ')[0]}! 👋
                                    </h1>
                                    <p className="text-slate-400">
                                        Let's set up your Accountrix account in 3 simple steps.
                                        It takes less than 2 minutes.
                                    </p>
                                </div>

                                <div className="grid gap-3 text-left">
                                    {[
                                        { icon: Building, text: 'Connect your e-conomic account', color: 'text-blue-400' },
                                        { icon: RefreshCw, text: 'Sync your clients automatically', color: 'text-purple-400' },
                                        { icon: BarChart3, text: 'See your portfolio risk dashboard', color: 'text-teal-400' },
                                    ].map((item, i) => (
                                        <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                                            <item.icon className={`h-5 w-5 ${item.color}`} />
                                            <span className="text-slate-300 text-sm">{item.text}</span>
                                        </div>
                                    ))}
                                </div>

                                <div className="flex gap-3">
                                    <Button
                                        onClick={() => setCurrentStep(2)}
                                        className="flex-1 bg-teal-600 hover:bg-teal-500 text-white"
                                    >
                                        Get Started <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" onClick={skipToDemo} className="text-slate-500 text-sm">
                                        Skip — use demo data
                                    </Button>
                                </div>
                            </div>
                        )}

                        {/* Step 2 — Connect e-conomic */}
                        {currentStep === 2 && (
                            <div className="space-y-6">
                                <div className="text-center">
                                    <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Building className="h-8 w-8 text-blue-400" />
                                    </div>
                                    <h2 className="text-xl font-bold text-white mb-2">Connect your e-conomic</h2>
                                    <p className="text-slate-400 text-sm">
                                        We need read-only access to your e-conomic to sync your client portfolio.
                                    </p>
                                </div>

                                <div className="bg-slate-800/50 rounded-lg p-4 space-y-3">
                                    <p className="text-slate-300 text-sm font-medium">How it works:</p>
                                    <div className="space-y-2">
                                        {[
                                            'Click "Connect E-conomic" below',
                                            'A new window opens — log in to e-conomic',
                                            'Click "Tilføj app" to grant access',
                                            'Come back here and go to the next step',
                                        ].map((step, i) => (
                                            <div key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                                <span className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs text-teal-400 font-bold flex-shrink-0">{i + 1}</span>
                                                {step}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="bg-teal-500/5 border border-teal-500/20 rounded-lg p-3 flex items-start gap-2">
                                    <Shield className="h-4 w-4 text-teal-400 mt-0.5 flex-shrink-0" />
                                    <p className="text-xs text-teal-300">
                                        Accountrix only reads your data — we never write, modify or delete anything in e-conomic.
                                    </p>
                                </div>

                                <div className="flex gap-3">
                                    <Button
                                        onClick={connectEconomic}
                                        className="flex-1 bg-teal-600 hover:bg-teal-500 text-white"
                                    >
                                        <ExternalLink className="mr-2 h-4 w-4" />
                                        Connect E-conomic
                                    </Button>
                                    <Button
                                        variant="outline"
                                        onClick={() => setCurrentStep(3)}
                                        className="border-slate-700 text-slate-400"
                                    >
                                        I've connected →
                                    </Button>
                                </div>

                                <button
                                    onClick={skipToDemo}
                                    className="w-full text-center text-xs text-slate-600 hover:text-slate-500"
                                >
                                    Skip for now — I'll connect later in Settings
                                </button>
                            </div>
                        )}

                        {/* Step 3 — Sync clients */}
                        {currentStep === 3 && (
                            <div className="space-y-6">
                                <div className="text-center">
                                    <div className="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <RefreshCw className="h-8 w-8 text-purple-400" />
                                    </div>
                                    <h2 className="text-xl font-bold text-white mb-2">Sync your clients</h2>
                                    <p className="text-slate-400 text-sm">
                                        Pull your client portfolio from e-conomic into your dashboard.
                                    </p>
                                </div>

                                <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                                    <p className="text-slate-400 text-sm mb-4">
                                        Click the button below to sync your clients. This takes about 10-30 seconds depending on how many clients you have.
                                    </p>
                                    <Button
                                        onClick={syncClients}
                                        disabled={syncing}
                                        className="bg-purple-600 hover:bg-purple-500 text-white px-8"
                                    >
                                        <RefreshCw className={`mr-2 h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
                                        {syncing ? 'Syncing your clients...' : 'Sync Clients Now'}
                                    </Button>
                                </div>

                                {syncResult && (
                                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 text-center">
                                        <CheckCircle className="h-8 w-8 text-green-400 mx-auto mb-2" />
                                        <p className="text-green-400 font-medium">{syncResult.synced} clients synced!</p>
                                    </div>
                                )}

                                <button
                                    onClick={skipToDemo}
                                    className="w-full text-center text-xs text-slate-600 hover:text-slate-500"
                                >
                                    Skip — use demo data for now
                                </button>
                            </div>
                        )}

                        {/* Step 4 — Ready */}
                        {currentStep === 4 && (
                            <div className="text-center space-y-6">
                                <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto">
                                    <CheckCircle className="h-10 w-10 text-green-400" />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2">You're all set! 🎉</h2>
                                    <p className="text-slate-400">
                                        {syncResult?.synced
                                            ? `${syncResult.synced} clients synced. Your portfolio dashboard is ready.`
                                            : 'Your Accountrix account is ready to use.'}
                                    </p>
                                </div>

                                <div className="grid gap-3 text-left">
                                    {[
                                        { icon: BarChart3, title: 'Portfolio Risk Dashboard', desc: 'See all clients ranked by risk', color: 'text-teal-400' },
                                        { icon: Bell, title: 'Exception Inbox', desc: 'Review flagged transactions', color: 'text-orange-400' },
                                        { icon: Clock, title: 'Pre-VAT Review', desc: 'Check deadline readiness', color: 'text-blue-400' },
                                    ].map((item, i) => (
                                        <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                                            <item.icon className={`h-5 w-5 ${item.color}`} />
                                            <div>
                                                <p className="text-white text-sm font-medium">{item.title}</p>
                                                <p className="text-slate-500 text-xs">{item.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <Button
                                    onClick={goToDashboard}
                                    className="w-full bg-teal-600 hover:bg-teal-500 text-white"
                                >
                                    Go to Portfolio Dashboard <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        )}

                    </CardContent>
                </Card>

                {/* Footer */}
                <p className="text-center text-xs text-slate-700 mt-6">
                    Need help? Email us at <a href="mailto:support@accountrix.dk" className="text-slate-500 hover:text-slate-400">support@accountrix.dk</a>
                </p>
            </div>
        </div>
    );
}
