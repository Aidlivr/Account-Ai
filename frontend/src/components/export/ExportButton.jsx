import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet } from 'lucide-react';
import { Button } from '../ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { toast } from 'sonner';
import { exportAPI } from '../../lib/api';

export const ExportButton = ({ tenantId, voucherIds = [], type = 'vouchers' }) => {
    const [exporting, setExporting] = useState(false);

    const handleExport = async (format) => {
        if (!tenantId) {
            toast.error('No company selected');
            return;
        }

        setExporting(true);
        try {
            const response = await exportAPI.exportVouchers(tenantId, {
                format,
                voucher_ids: voucherIds.length > 0 ? voucherIds : null
            });

            // Create download
            const blob = new Blob(
                [format === 'csv' ? response.data : atob(response.data.content)],
                { type: format === 'csv' ? 'text/csv' : 'application/pdf' }
            );
            
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `vouchers-export-${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            toast.success(`Exported ${type} as ${format.toUpperCase()}`);
        } catch (err) {
            console.error('Export error:', err);
            toast.error(`Failed to export as ${format.toUpperCase()}`);
        } finally {
            setExporting(false);
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button 
                    variant="outline" 
                    disabled={exporting}
                    data-testid="export-btn"
                >
                    {exporting ? (
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin mr-2" />
                    ) : (
                        <Download className="h-4 w-4 mr-2" />
                    )}
                    Export
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuItem 
                    onClick={() => handleExport('csv')}
                    data-testid="export-csv-btn"
                >
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem 
                    onClick={() => handleExport('pdf')}
                    data-testid="export-pdf-btn"
                >
                    <FileText className="h-4 w-4 mr-2" />
                    Export as PDF
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default ExportButton;
