import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export function formatCurrency(amount, currency = 'DKK') {
    if (amount === null || amount === undefined) return '-';
    return new Intl.NumberFormat('da-DK', {
        style: 'currency',
        currency: currency,
    }).format(amount);
}

export function formatDate(dateString) {
    if (!dateString) return '-';
    return new Intl.DateTimeFormat('da-DK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    }).format(new Date(dateString));
}

export function formatDateTime(dateString) {
    if (!dateString) return '-';
    return new Intl.DateTimeFormat('da-DK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(dateString));
}

export function getRiskLevel(score) {
    if (score < 30) return { level: 'low', label: 'Low Risk', color: 'text-success' };
    if (score < 70) return { level: 'medium', label: 'Medium Risk', color: 'text-warning' };
    return { level: 'high', label: 'High Risk', color: 'text-destructive' };
}

export function getStatusBadge(status) {
    const statusConfig = {
        processing: { label: 'Processing', variant: 'secondary' },
        review: { label: 'Pending Review', variant: 'warning' },
        approved: { label: 'Approved', variant: 'success' },
        rejected: { label: 'Rejected', variant: 'destructive' },
        error: { label: 'Error', variant: 'destructive' },
        matched: { label: 'Matched', variant: 'success' },
        unmatched: { label: 'Unmatched', variant: 'warning' },
        active: { label: 'Active', variant: 'success' },
        cancelled: { label: 'Cancelled', variant: 'destructive' },
    };
    return statusConfig[status] || { label: status, variant: 'secondary' };
}

export function truncateText(text, maxLength = 50) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

export function calculateConfidenceColor(confidence) {
    if (confidence >= 0.8) return 'text-success';
    if (confidence >= 0.5) return 'text-warning';
    return 'text-destructive';
}
