import type { ReactNode } from 'react';

type PageProps = {
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function Page({ title, eyebrow, actions, children }: PageProps) {
  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-zinc-200 pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          {eyebrow ? <div className="text-xs font-medium uppercase tracking-normal text-teal-700">{eyebrow}</div> : null}
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">{title}</h1>
        </div>
        {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
      </div>
      {children}
    </div>
  );
}
