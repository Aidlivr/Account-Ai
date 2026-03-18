import React, { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, Lock, User, ArrowRight, Building, Phone, Hash } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const registerSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
    role: z.enum(['sme_user', 'accountant']),
    firm_name: z.string().optional(),
    cvr_number: z.string().optional(),
    phone: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
});

export default function RegisterPage() {
    const { register: registerUser, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [selectedRole, setSelectedRole] = useState('accountant');

    const { register, handleSubmit, setValue, formState: { errors } } = useForm({
        resolver: zodResolver(registerSchema),
        defaultValues: { role: 'accountant' },
    });

    if (isAuthenticated) {
        return <Navigate to="/app/portfolio" replace />;
    }

    const onSubmit = async (data) => {
        setIsLoading(true);
        try {
            // Call register API directly to pass extra fields
            const response = await axios.post(`${BACKEND_URL}/api/auth/register`, {
                email: data.email,
                password: data.password,
                name: data.name,
                role: data.role,
                firm_name: data.firm_name || '',
                cvr_number: data.cvr_number || '',
                phone: data.phone || '',
            });

            setIsLoading(false);

            if (data.role === 'accountant') {
                navigate('/pending-approval');
                return;
            }

            // For non-accountants, log them in
            const result = await registerUser(data.email, data.password, data.name, data.role);
            if (result.success) {
                toast.success('Account created successfully!');
                navigate('/onboarding');
            }
        } catch (err) {
            setIsLoading(false);
            toast.error(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div
            className="min-h-screen flex items-center justify-center p-4"
            style={{
                backgroundImage: 'url(https://images.unsplash.com/photo-1768214033756-9506fa320aae?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwxfHxjYWxtJTIwbm9yd2F5JTIwbmF0dXJlJTIwbGFuZHNjYXBlJTIwZm9nfGVufDB8fHx8MTc3MTA5MTc4M3ww&ixlib=rb-4.1.0&q=85)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
            }}
        >
            <Card className="w-full max-w-lg glass-card animate-slide-up">
                <CardHeader className="text-center">
                    <CardTitle className="font-heading text-2xl">Create Account</CardTitle>
                    <CardDescription>Join Accountrix — Professional Portfolio Control</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">

                        {/* Account Type */}
                        <div className="space-y-2">
                            <Label>Account Type</Label>
                            <Select
                                defaultValue="accountant"
                                onValueChange={(value) => { setValue('role', value); setSelectedRole(value); }}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select account type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="accountant">Accounting Firm</SelectItem>
                                    <SelectItem value="sme_user">SME / Company</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Firm/Company Name */}
                        <div className="space-y-2">
                            <Label>{selectedRole === 'accountant' ? 'Accounting Firm Name' : 'Company Name'}</Label>
                            <div className="relative">
                                <Building className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder={selectedRole === 'accountant' ? 'Jensen & Partners Revision' : 'My Company ApS'}
                                    className="pl-10"
                                    {...register('firm_name')}
                                />
                            </div>
                        </div>

                        {/* CVR Number */}
                        <div className="space-y-2">
                            <Label>CVR Number</Label>
                            <div className="relative">
                                <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="12345678"
                                    className="pl-10"
                                    maxLength={8}
                                    {...register('cvr_number')}
                                />
                            </div>
                            <p className="text-xs text-muted-foreground">8-digit Danish company registration number</p>
                        </div>

                        {/* Full Name */}
                        <div className="space-y-2">
                            <Label>Contact Person</Label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Full name"
                                    className="pl-10"
                                    {...register('name')}
                                />
                            </div>
                            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                        </div>

                        {/* Email */}
                        <div className="space-y-2">
                            <Label>Work Email</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="email"
                                    placeholder="you@company.dk"
                                    className="pl-10"
                                    {...register('email')}
                                />
                            </div>
                            {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
                        </div>

                        {/* Phone */}
                        <div className="space-y-2">
                            <Label>Phone <span className="text-muted-foreground text-xs">(optional)</span></Label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="+45 12 34 56 78"
                                    className="pl-10"
                                    {...register('phone')}
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div className="space-y-2">
                            <Label>Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="password"
                                    placeholder="Min. 8 characters"
                                    className="pl-10"
                                    {...register('password')}
                                />
                            </div>
                            {errors.password && <p className="text-sm text-destructive">{errors.password.message}</p>}
                        </div>

                        {/* Confirm Password */}
                        <div className="space-y-2">
                            <Label>Confirm Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    className="pl-10"
                                    {...register('confirmPassword')}
                                />
                            </div>
                            {errors.confirmPassword && <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>}
                        </div>

                        {selectedRole === 'accountant' && (
                            <div className="bg-teal-500/10 border border-teal-500/20 rounded-lg p-3 text-xs text-teal-300">
                                ℹ️ Accounting firm accounts require approval. You will receive an email within 24 hours.
                            </div>
                        )}

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                            ) : (
                                <>Create Account <ArrowRight className="ml-2 h-4 w-4" /></>
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm">
                        <span className="text-muted-foreground">Already have an account? </span>
                        <Link to="/login" className="text-primary hover:underline font-medium">Sign in</Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
