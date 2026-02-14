import React, { useState, useEffect } from 'react';
import { X, Beaker, MessageSquare, Bug } from 'lucide-react';
import { Button } from '../ui/button';

export const BetaBanner = ({ onOpenFeedback, onOpenBugReport }) => {
    const [isVisible, setIsVisible] = useState(true);
    const [isDismissed, setIsDismissed] = useState(false);

    useEffect(() => {
        const dismissed = localStorage.getItem('beta-banner-dismissed');
        if (dismissed === 'true') {
            setIsDismissed(true);
            setIsVisible(false);
        }
    }, []);

    const handleDismiss = () => {
        setIsVisible(false);
        localStorage.setItem('beta-banner-dismissed', 'true');
        setIsDismissed(true);
    };

    const handleShowAgain = () => {
        setIsVisible(true);
        localStorage.removeItem('beta-banner-dismissed');
        setIsDismissed(false);
    };

    if (!isVisible) {
        return isDismissed ? (
            <button
                onClick={handleShowAgain}
                className="fixed bottom-4 right-4 z-50 bg-amber-500 text-white p-2 rounded-full shadow-lg hover:bg-amber-600 transition-colors"
                data-testid="show-beta-banner-btn"
                title="Show Beta Banner"
            >
                <Beaker className="h-5 w-5" />
            </button>
        ) : null;
    }

    return (
        <div 
            className="bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 text-white relative"
            data-testid="beta-banner"
        >
            <div className="max-w-screen-xl mx-auto px-4 py-3">
                <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                            <Beaker className="h-4 w-4" />
                            <span className="font-semibold text-sm">BETA</span>
                        </div>
                        <p className="text-sm font-medium">
                            You're using the beta version of AI Accounting Copilot. 
                            Your feedback helps us improve!
                        </p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="bg-white/20 hover:bg-white/30 text-white border-0"
                            onClick={onOpenFeedback}
                            data-testid="feedback-btn"
                        >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Send Feedback
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="bg-white/20 hover:bg-white/30 text-white border-0"
                            onClick={onOpenBugReport}
                            data-testid="bug-report-btn"
                        >
                            <Bug className="h-4 w-4 mr-2" />
                            Report Bug
                        </Button>
                        <button
                            onClick={handleDismiss}
                            className="p-1 rounded-full hover:bg-white/20 transition-colors ml-2"
                            data-testid="dismiss-beta-banner"
                            aria-label="Dismiss banner"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BetaBanner;
