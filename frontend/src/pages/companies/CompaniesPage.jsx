import React, { useState, useEffect } from 'react';
import { Building2, Plus, Settings, Users, Pencil } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTenant } from '../../contexts/TenantContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from '../../components/ui/dialog';
import { toast } from 'sonner';
import { formatDate } from '../../lib/utils';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function CompaniesPage() {
    const { tenants, currentTenant, selectTenant, createTenant, updateTenant, refreshTenants } = useTenant();
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const [editingTenant, setEditingTenant] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        cvr_number: '',
        address: '',
    });

    const handleCreate = async () => {
        if (!formData.name) {
            toast.error('Company name is required');
            return;
        }

        setIsLoading(true);
        const result = await createTenant(formData);
        setIsLoading(false);

        if (result.success) {
            toast.success('Company created successfully');
            setIsCreateOpen(false);
            setFormData({ name: '', cvr_number: '', address: '' });
        } else {
            toast.error(result.error);
        }
    };

    const handleEdit = async () => {
        if (!formData.name) {
            toast.error('Company name is required');
            return;
        }

        setIsLoading(true);
        const result = await updateTenant(editingTenant.id, formData);
        setIsLoading(false);

        if (result.success) {
            toast.success('Company updated successfully');
            setIsEditOpen(false);
            setEditingTenant(null);
            setFormData({ name: '', cvr_number: '', address: '' });
        } else {
            toast.error(result.error);
        }
    };

    const openEditDialog = (tenant) => {
        setEditingTenant(tenant);
        setFormData({
            name: tenant.name,
            cvr_number: tenant.cvr_number || '',
            address: tenant.address || '',
        });
        setIsEditOpen(true);
    };

    return (
        <div className="space-y-8" data-testid="companies-page">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-3xl font-bold">Companies</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage your companies and accounting integrations
                    </p>
                </div>
                <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                    <DialogTrigger asChild>
                        <Button data-testid="create-company-btn">
                            <Plus className="h-4 w-4 mr-2" />
                            Add Company
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New Company</DialogTitle>
                            <DialogDescription>
                                Add a new company to manage its accounting documents
                            </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Company Name *</Label>
                                <Input
                                    id="name"
                                    placeholder="Acme ApS"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    data-testid="company-name-input"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="cvr">CVR Number</Label>
                                <Input
                                    id="cvr"
                                    placeholder="12345678"
                                    maxLength={8}
                                    value={formData.cvr_number}
                                    onChange={(e) => setFormData({ ...formData, cvr_number: e.target.value })}
                                    data-testid="company-cvr-input"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="address">Address</Label>
                                <Input
                                    id="address"
                                    placeholder="Copenhagen, Denmark"
                                    value={formData.address}
                                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                                    data-testid="company-address-input"
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleCreate} disabled={isLoading} data-testid="submit-company-btn">
                                {isLoading ? 'Creating...' : 'Create Company'}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Companies Grid */}
            {tenants.length === 0 ? (
                <Card className="border-dashed border-2" data-testid="no-companies-card">
                    <CardContent className="flex flex-col items-center justify-center py-16">
                        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                            <Building2 className="h-8 w-8 text-primary" />
                        </div>
                        <h3 className="font-heading text-xl font-semibold mb-2">No Companies Yet</h3>
                        <p className="text-muted-foreground text-center mb-6 max-w-md">
                            Create your first company to start managing invoices and documents
                        </p>
                        <Button onClick={() => setIsCreateOpen(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Create Company
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <motion.div 
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    variants={container}
                    initial="hidden"
                    animate="show"
                >
                    {tenants.map((tenant) => (
                        <motion.div key={tenant.id} variants={item}>
                            <Card 
                                className={`cursor-pointer transition-all hover:shadow-md ${
                                    currentTenant?.id === tenant.id ? 'ring-2 ring-primary' : ''
                                }`}
                                onClick={() => selectTenant(tenant)}
                                data-testid={`company-card-${tenant.id}`}
                            >
                                <CardHeader className="flex flex-row items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                            <Building2 className="h-5 w-5 text-primary" />
                                        </div>
                                        <div>
                                            <CardTitle className="text-lg">{tenant.name}</CardTitle>
                                            {tenant.cvr_number && (
                                                <p className="text-sm text-muted-foreground font-mono">
                                                    CVR: {tenant.cvr_number}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    <Button 
                                        variant="ghost" 
                                        size="icon"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            openEditDialog(tenant);
                                        }}
                                        data-testid={`edit-company-${tenant.id}`}
                                    >
                                        <Pencil className="h-4 w-4" />
                                    </Button>
                                </CardHeader>
                                <CardContent>
                                    {tenant.address && (
                                        <p className="text-sm text-muted-foreground mb-3">{tenant.address}</p>
                                    )}
                                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                                        <span>Created {formatDate(tenant.created_at)}</span>
                                        {currentTenant?.id === tenant.id && (
                                            <span className="text-primary font-medium">Active</span>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>
            )}

            {/* Edit Dialog */}
            <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit Company</DialogTitle>
                        <DialogDescription>
                            Update company information
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="edit-name">Company Name *</Label>
                            <Input
                                id="edit-name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                data-testid="edit-company-name"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="edit-cvr">CVR Number</Label>
                            <Input
                                id="edit-cvr"
                                maxLength={8}
                                value={formData.cvr_number}
                                onChange={(e) => setFormData({ ...formData, cvr_number: e.target.value })}
                                data-testid="edit-company-cvr"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="edit-address">Address</Label>
                            <Input
                                id="edit-address"
                                value={formData.address}
                                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                                data-testid="edit-company-address"
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsEditOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleEdit} disabled={isLoading} data-testid="update-company-btn">
                            {isLoading ? 'Updating...' : 'Update Company'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
