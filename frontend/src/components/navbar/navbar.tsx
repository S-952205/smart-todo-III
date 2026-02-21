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
    <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link href="/dashboard" className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Todo App
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  href="/dashboard"
                  className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/dashboard/tasks"
                  className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
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