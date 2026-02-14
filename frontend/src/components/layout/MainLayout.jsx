import React, { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Sidebar } from './Sidebar';
import { Toaster } from '../ui/sonner';
import { BetaBanner } from '../beta/BetaBanner';
import { FeedbackDialog } from '../beta/FeedbackDialog';

export const MainLayout = () => {
    const { isAuthenticated, loading } = useAuth();
    const [feedbackOpen, setFeedbackOpen] = useState(false);
    const [bugReportOpen, setBugReportOpen] = useState(false);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-muted-foreground">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="min-h-screen bg-background">
            <BetaBanner 
                onOpenFeedback={() => setFeedbackOpen(true)}
                onOpenBugReport={() => setBugReportOpen(true)}
            />
            <Sidebar />
            <main className="ml-64 min-h-screen">
                <div className="p-8">
                    <Outlet />
                </div>
            </main>
            <Toaster position="top-right" richColors />
            
            {/* Feedback Dialogs */}
            <FeedbackDialog 
                open={feedbackOpen} 
                onOpenChange={setFeedbackOpen}
                type="feedback"
            />
            <FeedbackDialog 
                open={bugReportOpen} 
                onOpenChange={setBugReportOpen}
                type="bug"
            />
        </div>
    );
};
