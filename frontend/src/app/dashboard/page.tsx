'use client';

import React from 'react';
import { useAuth } from '@/context/auth-context';
import { useRouter } from 'next/navigation';
import { DashboardWithChat } from '@/app/components/dashboard/DashboardWithChat';
import { Task } from '@/types';

const DashboardPage: React.FC = () => {
  const { state } = useAuth();
  const router = useRouter();

  // For now, we'll show the dashboard with chat instead of redirecting
  // This allows users to access both tasks and chat from the main dashboard
  const initialTasks: Task[] = []; // In a real app, you'd fetch these from an API

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="py-8">
        <DashboardWithChat initialTasks={initialTasks} />
      </div>
    </div>
  );
};

export default DashboardPage;