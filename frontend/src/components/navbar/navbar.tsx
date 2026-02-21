'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { useRouter } from 'next/navigation';

const Navbar: React.FC = () => {
  const { state, logout } = useAuth();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <nav className="bg-black dark:bg-white shadow-sm border-b border-white/10 dark:border-white/10 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="sm:hidden mr-3 p-2 rounded-none text-white dark:text-black hover:bg-white/10 dark:hover:bg-black/10 transition-colors"
              aria-label="Toggle menu"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>

            <div className="flex-shrink-0">
              <Link href="/dashboard" className="text-2xl font-bold text-white dark:text-black" style={{ fontFamily: 'Satoshi, sans-serif' }}>
                TaskFlow
              </Link>
            </div>

            {/* Desktop navigation */}
            <div className="hidden sm:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  href="/dashboard"
                  className="text-white dark:text-black hover:bg-white/10 dark:hover:bg-black/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
                  style={{ fontFamily: 'Satoshi, sans-serif' }}
                >
                  Dashboard
                </Link>
                <Link
                  href="/dashboard/tasks"
                  className="text-white dark:text-black hover:bg-white/10 dark:hover:bg-black/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
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

        {/* Mobile menu dropdown */}
        {mobileMenuOpen && (
          <div className="sm:hidden pb-4">
            <div className="flex flex-col space-y-2">
              <Link
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="text-white dark:text-black hover:bg-white/10 dark:hover:bg-black/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
                style={{ fontFamily: 'Satoshi, sans-serif' }}
              >
                Dashboard
              </Link>
              <Link
                href="/dashboard/tasks"
                onClick={() => setMobileMenuOpen(false)}
                className="text-white dark:text-black hover:bg-white/10 dark:hover:bg-black/10 px-3 py-2 rounded-none text-sm font-medium transition-colors"
                style={{ fontFamily: 'Satoshi, sans-serif' }}
              >
                My Tasks
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;