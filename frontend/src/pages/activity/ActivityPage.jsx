import React, { useState, useEffect } from 'react';
import { Activity, Clock, FileText, CheckCircle, Edit2, User, Building2, CreditCard, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { activityAPI } from '../../lib/api';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../../components/ui/select';
import { formatDateTime } from '../../lib/utils';

const ACTIVITY_ICONS = {
    invoice_uploaded: FileText,
    ai_extraction_completed: Activity,
    user_edited_fields: Edit2,
    invoice_approved: CheckCircle,
    invoice_rejected: FileText,
    voucher_created: FileText,
    voucher_pushed: CheckCircle,
    user_registered: User,
    user_login: User,
    company_created: Building2,
    subscription_activated: CreditCard,
    provider_configured: Settings,
};

const ACTIVITY_LABELS = {
    invoice_uploaded: 'Invoice Uploaded',
    ai_extraction_completed: 'AI Extraction Completed',
    user_edited_fields: 'Fields Edited',
    invoice_approved: 'Invoice Approved',
    invoice_rejected: 'Invoice Rejected',
    voucher_created: 'Voucher Created',
    voucher_pushed: 'Voucher Pushed',
    user_registered: 'User Registered',
    user_login: 'User Login',
    company_created: 'Company Created',
    subscription_activated: 'Subscription Activated',
    provider_configured: 'Provider Configured',
};

export default function ActivityPage() {
    const { currentTenant } = useTenant();
    const navigate = useNavigate();
    const [activities, setActivities] = useState([]);
    const [timeSaved, setTimeSaved] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        if (currentTenant) {
            fetchData();
        } else {
            setLoading(false);
        }
    }, [currentTenant, filter]);

    const fetchData = async () => {
        try {
            const [activitiesRes, timeSavedRes] = await Promise.all([
                activityAPI.getLogs(currentTenant.id, filter === 'all' ? null : filter, 100),
                activityAPI.getTimeSaved(currentTenant.id, 30)
            ]);
            setActivities(activitiesRes.data);
            setTimeSaved(timeSavedRes.data);
        } catch (err) {
            console.error('Failed to fetch activity data:', err);
        } finally {
            setLoading(false);
        }
    };

    if (!currentTenant) {
        return (
            <div className="space-y-8" data-testid="activity-page">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Activity Log</h1>
                    <p className="text-muted-foreground mt-1">Track all actions and time saved</p>
                </div>
                <Card className="border-dashed border-2">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-heading text-xl font-semibold mb-2">No Company Selected</h3>
                        <Button onClick={() => navigate('/companies')}>Go to Companies</Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-8" data-testid="activity-page">
            {/* Header */}
            <div>
                <h1 className="font-heading text-3xl font-bold">Activity Log</h1>
                <p className="text-muted-foreground mt-1">
                    Track all actions for {currentTenant.name}
                </p>
            </div>

            {/* Time Saved Summary */}
            {timeSaved && (
                <Card className="bg-gradient-to-r from-primary/10 to-accent/10 border-primary/20">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground uppercase tracking-wider">Time Saved (Last 30 Days)</p>
                                <p className="text-4xl font-bold font-mono mt-2">
                                    {timeSaved.total_hours || 0} <span className="text-xl font-normal">hours</span>
                                </p>
                                <p className="text-sm text-muted-foreground mt-1">
                                    {Math.round(timeSaved.total_minutes || 0)} minutes of manual work automated
                                </p>
                            </div>
                            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                                <Clock className="h-10 w-10 text-primary" />
                            </div>
                        </div>
                        
                        {timeSaved.breakdown && Object.keys(timeSaved.breakdown).length > 0 && (
                            <div className="mt-6 pt-4 border-t border-primary/20">
                                <p className="text-sm font-medium mb-3">Breakdown by Activity</p>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {Object.entries(timeSaved.breakdown).map(([type, minutes]) => (
                                        <div key={type} className="text-sm">
                                            <p className="text-muted-foreground truncate">
                                                {ACTIVITY_LABELS[type] || type}
                                            </p>
                                            <p className="font-mono font-medium">{Math.round(minutes)} min</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Filter */}
            <div className="flex items-center gap-4">
                <Select value={filter} onValueChange={setFilter}>
                    <SelectTrigger className="w-48" data-testid="activity-filter">
                        <SelectValue placeholder="Filter activities" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Activities</SelectItem>
                        <SelectItem value="invoice_uploaded">Uploads</SelectItem>
                        <SelectItem value="ai_extraction_completed">AI Extractions</SelectItem>
                        <SelectItem value="invoice_approved">Approvals</SelectItem>
                        <SelectItem value="voucher_created">Vouchers</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {/* Activity Timeline */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5" />
                        Recent Activity
                    </CardTitle>
                    <CardDescription>
                        Chronological log of all system actions
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex items-center justify-center py-16">
                            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : activities.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                            <p className="text-muted-foreground">No activities recorded yet</p>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {activities.map((activity, idx) => {
                                const IconComponent = ACTIVITY_ICONS[activity.activity_type] || Activity;
                                const label = ACTIVITY_LABELS[activity.activity_type] || activity.activity_type;
                                
                                return (
                                    <motion.div
                                        key={activity.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.02 }}
                                        className="flex items-start gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                                            <IconComponent className="h-5 w-5 text-primary" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <p className="font-medium">{label}</p>
                                                {activity.time_saved_minutes && (
                                                    <Badge variant="secondary" className="text-xs">
                                                        <Clock className="h-3 w-3 mr-1" />
                                                        {activity.time_saved_minutes} min saved
                                                    </Badge>
                                                )}
                                            </div>
                                            {activity.details && Object.keys(activity.details).length > 0 && (
                                                <p className="text-sm text-muted-foreground mt-1 truncate">
                                                    {Object.entries(activity.details).slice(0, 3).map(([k, v]) => 
                                                        `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`
                                                    ).join(' • ')}
                                                </p>
                                            )}
                                        </div>
                                        <p className="text-sm text-muted-foreground whitespace-nowrap">
                                            {formatDateTime(activity.timestamp)}
                                        </p>
                                    </motion.div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
