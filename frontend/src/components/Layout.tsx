import type { ReactNode } from 'react';

type NavItem = {
  id: string;
  label: string;
};

type LayoutProps = {
  activeRoute: string;
  onNavigate: (route: string) => void;
  children: ReactNode;
};

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'factory', label: 'Factory' },
  { id: 'lines', label: 'Machine Lines' },
  { id: 'productTree', label: 'Product Tree' },
  { id: 'import', label: 'Import' },
  { id: 'scenarios', label: 'Scenarios' },
  { id: 'operators', label: 'Operators' },
  { id: 'inventory', label: 'Inventory' },
  { id: 'simulation', label: 'Simulation' },
  { id: 'schedule', label: 'Schedule' }
];

export function Layout({ activeRoute, onNavigate, children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-zinc-100 text-zinc-950">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-zinc-200 bg-white lg:block">
        <div className="border-b border-zinc-200 px-5 py-4">
          <div className="text-sm font-semibold">Digital Twin</div>
          <div className="mt-1 text-xs text-zinc-500">Factory simulation prototype</div>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`w-full rounded px-3 py-2 text-left text-sm ${
                activeRoute === item.id
                  ? 'bg-teal-700 text-white'
                  : 'text-zinc-700 hover:bg-zinc-100'
              }`}
              type="button"
              onClick={() => onNavigate(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-zinc-200 bg-white/95 px-4 py-3 backdrop-blur">
          <div className="flex flex-wrap items-center gap-2 lg:hidden">
            {navItems.map((item) => (
              <button
                key={item.id}
                className={`rounded px-2 py-1 text-xs ${
                  activeRoute === item.id ? 'bg-teal-700 text-white' : 'bg-zinc-100 text-zinc-700'
                }`}
                type="button"
                onClick={() => onNavigate(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="hidden text-sm font-medium text-zinc-700 lg:block">
            Local V1 Control Surface
          </div>
        </header>
        <main className="mx-auto max-w-[1600px] px-4 py-5 xl:px-6 2xl:px-8">{children}</main>
      </div>
    </div>
  );
}
