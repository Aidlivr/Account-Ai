import React, { useState } from 'react';
import { MessageSquare, Bug, Send, Star } from 'lucide-react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { toast } from 'sonner';
import { feedbackAPI } from '../../lib/api';

export const FeedbackDialog = ({ open, onOpenChange, type = 'feedback' }) => {
    const [rating, setRating] = useState(0);
    const [feedbackText, setFeedbackText] = useState('');
    const [category, setCategory] = useState('general');
    const [pageContext, setPageContext] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const isBugReport = type === 'bug';

    const categories = isBugReport 
        ? ['ai_extraction', 'ui_issue', 'performance', 'data_loss', 'other']
        : ['general', 'feature_request', 'usability', 'praise', 'other'];

    const handleSubmit = async () => {
        if (!feedbackText.trim()) {
            toast.error('Please enter your feedback');
            return;
        }

        setSubmitting(true);
        try {
            await feedbackAPI.submit({
                type: isBugReport ? 'bug_report' : 'feedback',
                rating: isBugReport ? null : rating,
                category,
                message: feedbackText,
                page_context: pageContext || window.location.pathname,
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString()
            });
            
            toast.success(isBugReport 
                ? 'Bug report submitted. Thank you!' 
                : 'Thank you for your feedback!'
            );
            
            // Reset form
            setRating(0);
            setFeedbackText('');
            setCategory('general');
            setPageContext('');
            onOpenChange(false);
        } catch (err) {
            toast.error('Failed to submit. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md" data-testid="feedback-dialog">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        {isBugReport ? (
                            <>
                                <Bug className="h-5 w-5 text-red-500" />
                                Report a Bug
                            </>
                        ) : (
                            <>
                                <MessageSquare className="h-5 w-5 text-primary" />
                                Send Feedback
                            </>
                        )}
                    </DialogTitle>
                    <DialogDescription>
                        {isBugReport 
                            ? 'Help us fix issues by describing what went wrong'
                            : 'Share your thoughts to help us improve'
                        }
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Rating (only for feedback) */}
                    {!isBugReport && (
                        <div className="space-y-2">
                            <Label>How's your experience so far?</Label>
                            <div className="flex gap-1">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <button
                                        key={star}
                                        onClick={() => setRating(star)}
                                        className="p-1 transition-colors"
                                        data-testid={`rating-star-${star}`}
                                    >
                                        <Star 
                                            className={`h-6 w-6 ${
                                                star <= rating 
                                                    ? 'text-yellow-400 fill-yellow-400' 
                                                    : 'text-muted-foreground'
                                            }`}
                                        />
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Category */}
                    <div className="space-y-2">
                        <Label htmlFor="category">
                            {isBugReport ? 'Bug Category' : 'Feedback Category'}
                        </Label>
                        <select
                            id="category"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                            data-testid="feedback-category"
                        >
                            {categories.map((cat) => (
                                <option key={cat} value={cat}>
                                    {cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Bug-specific: Page context */}
                    {isBugReport && (
                        <div className="space-y-2">
                            <Label htmlFor="pageContext">Where did this happen?</Label>
                            <Input
                                id="pageContext"
                                placeholder="e.g., Documents page, during invoice upload"
                                value={pageContext}
                                onChange={(e) => setPageContext(e.target.value)}
                                data-testid="bug-page-context"
                            />
                        </div>
                    )}

                    {/* Message */}
                    <div className="space-y-2">
                        <Label htmlFor="feedbackText">
                            {isBugReport ? 'Describe the bug' : 'Your feedback'}
                        </Label>
                        <Textarea
                            id="feedbackText"
                            placeholder={isBugReport 
                                ? 'What happened? What did you expect to happen?'
                                : 'Share your thoughts, suggestions, or ideas...'
                            }
                            value={feedbackText}
                            onChange={(e) => setFeedbackText(e.target.value)}
                            rows={4}
                            data-testid="feedback-text"
                        />
                    </div>

                    {/* AI Error specific hint */}
                    {isBugReport && category === 'ai_extraction' && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
                            <p className="font-medium mb-1">AI Extraction Issue?</p>
                            <p>Please describe:</p>
                            <ul className="list-disc list-inside ml-2 text-xs mt-1">
                                <li>What data was extracted incorrectly?</li>
                                <li>What should the correct value be?</li>
                                <li>Any unusual formatting in your invoice?</li>
                            </ul>
                        </div>
                    )}
                </div>

                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={submitting}
                    >
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleSubmit} 
                        disabled={submitting}
                        data-testid="submit-feedback-btn"
                    >
                        {submitting ? (
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        ) : (
                            <Send className="h-4 w-4 mr-2" />
                        )}
                        Submit
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default FeedbackDialog;
