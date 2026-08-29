'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Bot, LogIn, UserPlus } from 'lucide-react';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'student' | 'admin'>('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup';
    const payload = isLogin ? { email, password } : { name, email, password, role };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const responseText = await res.text();
      let data: any = {};
      try {
        data = JSON.parse(responseText);
      } catch {
        if (!res.ok) {
          throw new Error(`Server connection error (${res.status}). Please check if the backend server is running.`);
        }
      }

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      login(data.access_token, data.refresh_token, {
        name: data.name || name || 'User',
        email: email,
        role: data.role,
      });

      if (data.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (userType: 'student' | 'admin') => {
    if (userType === 'student') {
      setEmail('student@campusmind.edu');
      setPassword('student123');
    } else {
      setEmail('admin@campusmind.edu');
      setPassword('admin123');
    }
    setIsLogin(true);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-blue-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg shadow-blue-500/30">
            <Bot className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">
            {isLogin ? 'Sign In to CampusMind' : 'Create an Account'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Access strictly-grounded college knowledge
          </p>
        </div>

        {/* Demo Fast Login Helpers */}
        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 mb-6">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Quick Fill Demo Accounts:
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('student')}
              className="flex-1 py-1.5 px-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-100"
            >
              🎓 Student Demo
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('admin')}
              className="flex-1 py-1.5 px-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-purple-700 hover:bg-purple-50 border-purple-200"
            >
              🛡️ Admin Demo
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@campusmind.edu"
              className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Role
              </label>
              <div className="flex gap-4 mt-1">
                <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input
                    type="radio"
                    name="role"
                    value="student"
                    checked={role === 'student'}
                    onChange={() => setRole('student')}
                  />
                  Student
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input
                    type="radio"
                    name="role"
                    value="admin"
                    checked={role === 'admin'}
                    onChange={() => setRole('admin')}
                  />
                  Admin
                </label>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl shadow-lg shadow-blue-600/20 transition flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
          >
            {isLogin ? <LogIn className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
            {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-sm text-blue-600 hover:underline font-medium"
          >
            {isLogin
              ? "Don't have an account? Sign Up"
              : 'Already have an account? Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}
