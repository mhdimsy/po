export function Status({ value }: { value: string | number | null | undefined }) {
  return (
    <span className="inline-flex rounded border border-zinc-200 bg-white px-2 py-1 text-xs font-medium text-zinc-700">
      {value ?? 'None'}
    </span>
  );
}

export function ErrorState({ error }: { error: unknown }) {
  return (
    <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
      {error instanceof Error ? error.message : 'Request failed'}
    </div>
  );
}

export function EmptyState({ label }: { label: string }) {
  return <div className="rounded border border-zinc-200 bg-white p-4 text-sm text-zinc-500">{label}</div>;
}
