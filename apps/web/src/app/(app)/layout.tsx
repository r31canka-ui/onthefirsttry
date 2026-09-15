'use client';

import { ReactNode, useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import clsx from 'clsx';
import { useAuth } from '@/lib/auth-context';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', permission: 'reports.read' },
  { href: '/contacts', label: 'Contacts', permission: 'contacts.read' },
  { href: '/calendar', label: 'Calendar', permission: null },
  { href: '/staff', label: 'Staff', permission: 'staff.manage' },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout, hasPermission } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/login');
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-gray-500">
        Loading...
      </div>
    );
  }

  const visibleNav = NAV_ITEMS.filter((item) => !item.permission || hasPermission(item.permission));

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 md:hidden">
        <span className="font-semibold">Clinic CRM</span>
        <button
          onClick={() => setMobileOpen((v) => !v)}
          className="rounded-md p-2 text-gray-600 hover:bg-gray-100"
          aria-label="Toggle menu"
        >
          <MenuIcon />
        </button>
      </header>

      <nav
        className={clsx(
          'w-full flex-col border-b border-gray-200 bg-white md:flex md:w-56 md:border-b-0 md:border-r md:min-h-screen',
          mobileOpen ? 'flex' : 'hidden md:flex',
        )}
      >
        <div className="hidden px-4 py-4 text-lg font-semibold md:block">Clinic CRM</div>
        <div className="flex flex-1 flex-col gap-1 px-2 py-2">
          {visibleNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={clsx(
                'rounded-md px-3 py-2 text-sm font-medium',
                pathname?.startsWith(item.href)
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100',
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
        <div className="border-t border-gray-200 px-4 py-3 text-sm">
          <div className="font-medium text-gray-900">{user.fullName}</div>
          <div className="truncate text-gray-500">{user.email}</div>
          <button onClick={logout} className="mt-2 text-blue-600 hover:underline">
            Log out
          </button>
        </div>
      </nav>

      <main className="flex-1 p-4 md:p-8">{children}</main>
    </div>
  );
}

function MenuIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18M3 12h18M3 18h18" strokeLinecap="round" />
    </svg>
  );
}
