import type { ButtonHTMLAttributes, ReactNode } from 'react';

type LoadingButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'dark';
  children: ReactNode;
};

const variantClass = {
  primary: 'bg-teal-700 text-white hover:bg-teal-800 disabled:bg-zinc-300',
  secondary: 'border border-zinc-300 bg-white text-zinc-800 hover:bg-zinc-50 disabled:text-zinc-400',
  danger: 'bg-red-700 text-white hover:bg-red-800 disabled:bg-zinc-300',
  dark: 'bg-zinc-900 text-white hover:bg-zinc-800 disabled:bg-zinc-300'
};

export function LoadingButton({ loading = false, variant = 'primary', children, className = '', disabled, ...props }: LoadingButtonProps) {
  return (
    <button
      className={`inline-flex min-h-9 items-center justify-center gap-2 rounded px-3 py-2 text-sm font-medium transition ${variantClass[variant]} ${className}`}
      disabled={disabled || loading}
      type="button"
      {...props}
    >
      {loading ? <span className="loading-spinner" aria-hidden="true" /> : null}
      <span>{children}</span>
    </button>
  );
}
