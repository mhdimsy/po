import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiGet, apiPost } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState } from '../../components/Status';
import type { InventoryBalance, InventoryItem } from '../../types/api';

export function InventoryPage() {
  const queryClient = useQueryClient();
  const items = useQuery({ queryKey: ['inventory-items'], queryFn: () => apiGet<InventoryItem[]>('/synthetic/inventory-items?limit=100') });
  const balances = useQuery({ queryKey: ['inventory-balances'], queryFn: () => apiGet<InventoryBalance[]>('/synthetic/inventory-balances?limit=100') });
  const generateInventory = useMutation({
    mutationFn: () => apiPost('/synthetic/inventory/generate', { preset: 'Normal' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory-items'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-balances'] });
    }
  });
  const generateSuppliers = useMutation({ mutationFn: () => apiPost('/synthetic/suppliers/generate', { preset: 'Mixed', suppliers_per_item: 3 }) });

  return (
    <Page
      title="Inventory"
      eyebrow="Synthetic materials"
      actions={(
        <>
          <button className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white" type="button" onClick={() => generateInventory.mutate()}>Generate Inventory</button>
          <button className="rounded border border-zinc-300 bg-white px-3 py-2 text-sm font-medium" type="button" onClick={() => generateSuppliers.mutate()}>Generate Suppliers</button>
        </>
      )}
    >
      {items.error ? <ErrorState error={items.error} /> : null}
      <section className="grid gap-4 lg:grid-cols-2">
        <div className="overflow-hidden rounded border border-zinc-200 bg-white">
          {items.data?.length ? (
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500"><tr><th className="p-3">Code</th><th className="p-3">Title</th><th className="p-3">Unit</th></tr></thead>
              <tbody>{items.data.map((item) => <tr key={item.id} className="border-t border-zinc-200"><td className="p-3 font-medium">{item.code}</td><td className="p-3">{item.title}</td><td className="p-3">{item.unit}</td></tr>)}</tbody>
            </table>
          ) : <EmptyState label="No inventory items." />}
        </div>
        <div className="overflow-hidden rounded border border-zinc-200 bg-white">
          {balances.data?.length ? (
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500"><tr><th className="p-3">Item</th><th className="p-3">On hand</th><th className="p-3">Reserved</th><th className="p-3">Preset</th></tr></thead>
              <tbody>{balances.data.map((balance) => <tr key={balance.id} className="border-t border-zinc-200"><td className="p-3">{balance.inventory_item_id}</td><td className="p-3">{balance.on_hand_qty}</td><td className="p-3">{balance.reserved_qty}</td><td className="p-3">{balance.preset}</td></tr>)}</tbody>
            </table>
          ) : <EmptyState label="No balances." />}
        </div>
      </section>
    </Page>
  );
}
