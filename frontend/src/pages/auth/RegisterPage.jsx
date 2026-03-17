import React, { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, Lock, User, ArrowRight } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../../components/ui/select';
import { toast } from 'sonner';

const registerSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    confirmPassword: z.string(),
    role: z.enum(['sme_user', 'accountant']),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
});

export default function RegisterPage() {
    const { register: registerUser, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
        resolver: zodResolver(registerSchema),
        defaultValues: {
            role: 'sme_user',
        },
    });

    if (isAuthenticated) {
        return <Navigate to="/app/portfolio" replace />;
    }

    const onSubmit = async (data) => {
        setIsLoading(true);
        const result = await registerUser(data.email, data.password, data.name, data.role);
        setIsLoading(false);

        if (result.success) {
            // Accountants go through approval — redirect to pending page
            if (data.role === 'accountant') {
                navigate('/pending-approval');
                return;
            }
            toast.success('Account created successfully!');
            navigate('/onboarding');
        } else {
            toast.error(result.error);
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
            <Card className="w-full max-w-md glass-card animate-slide-up" data-testid="register-card">
                <CardHeader className="text-center">
                    <CardTitle className="font-heading text-2xl">Create Account</CardTitle>
                    <CardDescription>Start your AI-powered accounting journey</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Full Name</Label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="name"
                                    placeholder="John Doe"
                                    className="pl-10"
                                    {...register('name')}
                                    data-testid="register-name"
                                />
                            </div>
                            {errors.name && (
                                <p className="text-sm text-destructive">{errors.name.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@company.dk"
                                    className="pl-10"
                                    {...register('email')}
                                    data-testid="register-email"
                                />
                            </div>
                            {errors.email && (
                                <p className="text-sm text-destructive">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="role">Account Type</Label>
                            <Select 
                                defaultValue="sme_user" 
                                onValueChange={(value) => setValue('role', value)}
                            >
                                <SelectTrigger data-testid="register-role">
                                    <SelectValue placeholder="Select account type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="sme_user">SME User</SelectItem>
                                    <SelectItem value="accountant">Accountant</SelectItem>
                                </SelectContent>
                            </Select>
                            {errors.role && (
                                <p className="text-sm text-destructive">{errors.role.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    className="pl-10"
                                    {...register('password')}
                                    data-testid="register-password"
                                />
                            </div>
                            {errors.password && (
                                <p className="text-sm text-destructive">{errors.password.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="confirmPassword"
                                    type="password"
                                    placeholder="••••••••"
                                    className="pl-10"
                                    {...register('confirmPassword')}
                                    data-testid="register-confirm-password"
                                />
                            </div>
                            {errors.confirmPassword && (
                                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
                            )}
                        </div>

                        <Button 
                            type="submit" 
                            className="w-full" 
                            disabled={isLoading}
                            data-testid="register-submit"
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                            ) : (
                                <>
                                    Create Account
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm">
                        <span className="text-muted-foreground">Already have an account? </span>
                        <Link to="/login" className="text-primary hover:underline font-medium" data-testid="login-link">
                            Sign in
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
