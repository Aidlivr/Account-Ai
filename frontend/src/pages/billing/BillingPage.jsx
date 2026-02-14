import React, { useState, useEffect } from 'react';
import { CreditCard, Check, Sparkles, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { billingAPI } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { toast } from 'sonner';
import { formatCurrency, formatDate } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function BillingPage() {
    const [plans, setPlans] = useState([]);
    const [subscription, setSubscription] = useState(null);
    const [currentPlan, setCurrentPlan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [subscribing, setSubscribing] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [plansRes, subRes] = await Promise.all([
                    billingAPI.getPlans(),
                    billingAPI.getCurrentSubscription()
                ]);
                setPlans(plansRes.data);
                setSubscription(subRes.data.subscription);
                setCurrentPlan(subRes.data.plan);
            } catch (err) {
                console.error('Failed to fetch billing data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleSubscribe = async (planId) => {
        setSubscribing(planId);
        try {
            await billingAPI.subscribe(planId);
            toast.success('Subscription activated!');
            // Refresh data
            const subRes = await billingAPI.getCurrentSubscription();
            setSubscription(subRes.data.subscription);
            setCurrentPlan(subRes.data.plan);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Subscription failed');
        } finally {
            setSubscribing(null);
        }
    };

    const handleCancel = async () => {
        try {
            await billingAPI.cancelSubscription();
            toast.success('Subscription cancelled');
            setSubscription(null);
            setCurrentPlan(null);
        } catch (err) {
            toast.error('Failed to cancel subscription');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-16">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8" data-testid="billing-page">
            {/* Header */}
            <div>
                <h1 className="font-heading text-3xl font-bold">Billing & Plans</h1>
                <p className="text-muted-foreground mt-1">
                    Manage your subscription and billing
                </p>
            </div>

            {/* Current Subscription */}
            {subscription && currentPlan && (
                <Card className="border-primary/50" data-testid="current-subscription">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    <Sparkles className="h-5 w-5 text-primary" />
                                    Current Plan: {currentPlan.name}
                                </CardTitle>
                                <CardDescription className="mt-1">
                                    Active since {formatDate(subscription.current_period_start)}
                                </CardDescription>
                            </div>
                            <Badge variant="success">Active</Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-3xl font-bold font-mono">
                                    {formatCurrency(currentPlan.price, currentPlan.currency)}
                                    <span className="text-base font-normal text-muted-foreground">/month</span>
                                </p>
                            </div>
                            <Button variant="outline" onClick={handleCancel} data-testid="cancel-subscription-btn">
                                Cancel Subscription
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Plans Grid */}
            <motion.div 
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
                variants={container}
                initial="hidden"
                animate="show"
            >
                {plans.map((plan) => {
                    const isCurrentPlan = currentPlan?.id === plan.id;
                    const isProfessional = plan.id === 'professional';
                    
                    return (
                        <motion.div key={plan.id} variants={item}>
                            <Card 
                                className={`relative overflow-hidden ${
                                    isProfessional ? 'border-primary shadow-lg' : ''
                                } ${isCurrentPlan ? 'ring-2 ring-primary' : ''}`}
                                data-testid={`plan-${plan.id}`}
                            >
                                {isProfessional && (
                                    <div className="absolute top-0 right-0">
                                        <Badge className="rounded-none rounded-bl-lg">Popular</Badge>
                                    </div>
                                )}
                                <CardHeader>
                                    <CardTitle>{plan.name}</CardTitle>
                                    <CardDescription>
                                        <span className="text-3xl font-bold font-mono text-foreground">
                                            {formatCurrency(plan.price, plan.currency)}
                                        </span>
                                        <span className="text-muted-foreground">/month</span>
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <ul className="space-y-3">
                                        {plan.features.map((feature, idx) => (
                                            <li key={idx} className="flex items-center gap-2 text-sm">
                                                <Check className="h-4 w-4 text-success shrink-0" />
                                                <span>{feature}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </CardContent>
                                <CardFooter>
                                    {isCurrentPlan ? (
                                        <Button disabled className="w-full" variant="outline">
                                            Current Plan
                                        </Button>
                                    ) : (
                                        <Button 
                                            className="w-full"
                                            variant={isProfessional ? 'default' : 'outline'}
                                            onClick={() => handleSubscribe(plan.id)}
                                            disabled={subscribing === plan.id || !!subscription}
                                            data-testid={`subscribe-${plan.id}`}
                                        >
                                            {subscribing === plan.id ? (
                                                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                                            ) : subscription ? (
                                                'Change Plan'
                                            ) : (
                                                'Subscribe'
                                            )}
                                        </Button>
                                    )}
                                </CardFooter>
                            </Card>
                        </motion.div>
                    );
                })}
            </motion.div>

            {/* Payment Info */}
            <Card>
                <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                            <CreditCard className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div>
                            <h3 className="font-semibold">Secure Payments</h3>
                            <p className="text-sm text-muted-foreground mt-1">
                                All payments are processed securely through Stripe. Your payment information is never stored on our servers.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
