import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Mail, Shield } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../contexts/AuthContext';

export default function PendingApprovalPage() {
    const { logout } = useAuth();

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
            <div className="w-full max-w-md">

                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-2 mb-2">
                        <Shield className="h-8 w-8 text-teal-400" />
                        <span className="text-2xl font-bold text-white">Accountrix</span>
                    </div>
                </div>

                <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-8 text-center space-y-6">

                        <div className="w-20 h-20 bg-yellow-500/10 rounded-full flex items-center justify-center mx-auto">
                            <Clock className="h-10 w-10 text-yellow-400" />
                        </div>

                        <div>
                            <h1 className="text-2xl font-bold text-white mb-3">
                                Account Pending Approval
                            </h1>
                            <p className="text-slate-400">
                                Thank you for registering! Your account is currently being reviewed.
                                You will receive an email once your account is approved.
                            </p>
                        </div>

                        <div className="bg-slate-800/50 rounded-lg p-4 space-y-3 text-left">
                            <p className="text-slate-300 text-sm font-medium">What happens next:</p>
                            <div className="space-y-2">
                                {[
                                    'We review your registration (usually within 24 hours)',
                                    'You receive an approval email',
                                    'Log in and connect your e-conomic account',
                                    'Your client portfolio syncs automatically',
                                ].map((step, i) => (
                                    <div key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                        <span className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs text-teal-400 font-bold flex-shrink-0">{i + 1}</span>
                                        {step}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center gap-2 text-sm text-slate-500 justify-center">
                            <Mail className="h-4 w-4" />
                            <span>Questions? Email <a href="mailto:support@accountrix.dk" className="text-teal-400 hover:underline">support@accountrix.dk</a></span>
                        </div>

                        <Button
                            variant="ghost"
                            className="text-slate-500 text-sm w-full"
                            onClick={logout}
                        >
                            Back to login
                        </Button>

                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
