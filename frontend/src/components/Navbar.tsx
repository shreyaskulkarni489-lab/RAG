'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Bot, LogOut, ShieldCheck, UserCircle, MessageSquare } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-blue-600 text-white p-2 rounded-xl">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <span className="font-bold text-xl text-slate-800 tracking-tight">CampusMind</span>
            <span className="text-xs ml-2 px-2 py-0.5 bg-blue-50 text-blue-700 font-medium rounded-full border border-blue-200">
              RAG AI
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-4">
          {user ? (
            <>
              <Link
                href="/"
                className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-blue-600"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </Link>
              {user.role === 'admin' && (
                <Link
                  href="/admin"
                  className="flex items-center gap-1.5 text-sm font-medium text-purple-700 hover:text-purple-900 bg-purple-50 px-3 py-1.5 rounded-lg border border-purple-200"
                >
                  <ShieldCheck className="w-4 h-4" />
                  Admin Dashboard
                </Link>
              )}
              <div className="flex items-center gap-2 border-l pl-4 border-slate-200">
                <UserCircle className="w-5 h-5 text-slate-500" />
                <span className="text-sm font-medium text-slate-700">{user.name}</span>
                <span className="text-xs uppercase px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded">
                  {user.role}
                </span>
                <button
                  onClick={logout}
                  title="Logout"
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <Link
              href="/login"
              className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
