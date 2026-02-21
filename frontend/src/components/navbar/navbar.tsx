'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { useRouter } from 'next/navigation';

const Navbar: React.FC = () => {
  const { state, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <nav className="bg-[#25343F] dark:bg-[#25343F] shadow-sm border-b border-white/10 dark:border-white/10 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link href="/dashboard" className="text-2xl font-bold text-white dark:text-white" style={{ fontFamily: 'Satoshi, sans-serif' }}>
                TaskFlow
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  href="/dashboard"
                  className="text-white/80 dark:text-white/80 hover:bg-white/10 dark:hover:bg-white/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
                  style={{ fontFamily: 'Satoshi, sans-serif' }}
                >
                  Dashboard
                </Link>
                <Link
                  href="/dashboard/tasks"
                  className="text-white/80 dark:text-white/80 hover:bg-white/10 dark:hover:bg-white/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
                  style={{ fontFamily: 'Satoshi, sans-serif' }}
                >
                  My Tasks
                </Link>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <UserAvatar
              name={state.user?.name}
              email={state.user?.email}
              size="md"
              showDropdown={true}
              onLogout={handleLogout}
            />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;