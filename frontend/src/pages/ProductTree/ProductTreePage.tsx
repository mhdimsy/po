import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { apiGet } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { ProductTreeNode, ProductTreeResponse, Scenario } from '../../types/api';

export function ProductTreePage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [rootOrderId, setRootOrderId] = useState('');
  const [rootLimit, setRootLimit] = useState(10);
  const [refreshSeconds, setRefreshSeconds] = useState(5);
  const [zoom, setZoom] = useState(0.9);
  const refetchInterval = Math.max(1, refreshSeconds) * 1000;

  const scenarios = useQuery({ queryKey: ['tree-scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios'), refetchInterval });
  const activeScenarioId = scenarioId ?? scenarios.data?.[0]?.id ?? null;
  const tree = useQuery({
    queryKey: ['product-tree', activeScenarioId, rootOrderId, rootLimit],
    queryFn: () => apiGet<ProductTreeResponse>(productTreePath(activeScenarioId, rootOrderId, rootLimit)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const totals = useMemo(() => summarizeTree(tree.data?.roots ?? []), [tree.data]);

  return (
    <Page
      title="Product Tree"
      eyebrow="Manufacturing order structure"
      actions={
        <>
          <select
            className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm"
            value={scenarioId ?? ''}
            onChange={(event) => setScenarioId(event.target.value ? Number(event.target.value) : null)}
          >
            <option value="">Latest scenario</option>
            {scenarios.data?.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
          <input
            className="h-9 w-36 rounded border border-zinc-300 bg-white px-3 text-sm"
            placeholder="Order id"
            value={rootOrderId}
            onChange={(event) => setRootOrderId(event.target.value)}
          />
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Roots</span>
            <input
              className="w-12 bg-transparent text-right outline-none"
              min={1}
              max={100}
              type="number"
              value={rootLimit}
              onChange={(event) => setRootLimit(Number(event.target.value))}
            />
          </label>
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Refresh</span>
            <input
              className="w-12 bg-transparent text-right outline-none"
              min={1}
              max={60}
              type="number"
              value={refreshSeconds}
              onChange={(event) => setRefreshSeconds(Number(event.target.value))}
            />
            <span className="text-zinc-500">s</span>
          </label>
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Zoom</span>
            <input
              className="w-24 accent-teal-700"
              min={0.55}
              max={1.25}
              step={0.05}
              type="range"
              value={zoom}
              onChange={(event) => setZoom(Number(event.target.value))}
            />
          </label>
        </>
      }
    >
      {tree.error ? <ErrorState error={tree.error} /> : null}

      <section className="grid gap-4 md:grid-cols-4">
        <TreeMetric label="Orders" value={totals.orders} subLabel={`${tree.data?.total_orders_in_scope ?? 0} in scenario`} />
        <TreeMetric label="Running" value={totals.running} subLabel="orders with active operations" />
        <TreeMetric label="Finished" value={totals.finished} subLabel="orders fully completed" />
        <TreeMetric label="Blocked" value={totals.blocked} subLabel={tree.isFetching ? 'refreshing now' : `refresh ${refreshSeconds}s`} />
      </section>

      <section className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
        <div className="mb-4 flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-base font-semibold">Schematic order tree</h2>
            <div className="mt-1 text-sm text-zinc-500">Parent orders branch into their child manufacturing orders. Each node shows the current production state.</div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Status value={activeScenarioId ? `Scenario ${activeScenarioId}` : 'No scenario'} />
            <Status value={`${tree.data?.root_count ?? 0} roots`} />
            <Status value={`${Math.round(zoom * 100)}% zoom`} />
            <Status value={tree.isFetching ? 'Refreshing' : 'Live'} />
          </div>
        </div>
        <div className="mb-4 flex flex-wrap gap-2 text-xs">
          <LegendItem label="Running" className="bg-blue-600" />
          <LegendItem label="Queued" className="bg-amber-500" />
          <LegendItem label="Finished" className="bg-emerald-600" />
          <LegendItem label="Blocked" className="bg-red-600" />
          <LegendItem label="Not seeded" className="bg-zinc-400" />
        </div>

        {tree.data?.roots.length ? (
          <div className="tree-canvas overflow-auto rounded border border-zinc-200 bg-zinc-50 p-6">
            <div className="flex min-w-max origin-top-left flex-col gap-8" style={{ transform: `scale(${zoom})` }}>
              {tree.data.roots.map((root) => (
                <TreeNodeView key={root.order_id} node={root} depth={0} />
              ))}
            </div>
          </div>
        ) : (
          <EmptyState label="No product tree found for this scenario/order. Try another order id or rebuild the demo database." />
        )}
      </section>
    </Page>
  );
}

function TreeNodeView({ node, depth }: { node: ProductTreeNode; depth: number }) {
  return (
    <div className="tree-row flex items-start">
      <OrderNodeCard node={node} depth={depth} />
      {node.children.length ? (
        <div className="tree-children relative flex flex-col gap-4 pl-12">
          {node.children.map((child) => (
            <div key={child.order_id} className="tree-child relative">
              <TreeNodeView node={child} depth={depth + 1} />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function OrderNodeCard({ node, depth }: { node: ProductTreeNode; depth: number }) {
  const summary = node.operation_summary;
  const progress = summary.total ? Math.round((summary.finished / summary.total) * 100) : 0;
  const activeCount = summary.running + summary.setup;
  return (
    <div className={`tree-node w-80 shrink-0 rounded border bg-white p-4 shadow-sm ${statusBorder(node.computed_status)}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${statusDot(node.computed_status)} ${node.computed_status === 'Running' ? 'status-pulse' : ''}`} />
            <div className="truncate text-sm font-semibold">Order {node.order_id}</div>
          </div>
          <div className="mt-1 truncate text-xs text-zinc-500">{node.order_code ?? node.product_code ?? 'No code'}</div>
        </div>
        <Status value={node.computed_status} />
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded bg-zinc-100">
        <div className={`h-full rounded ${progressColor(node.computed_status)}`} style={{ width: `${Math.max(4, progress)}%` }} />
      </div>
      <div className="mt-3 grid grid-cols-4 gap-2 text-xs">
        <TinyStat label="Run" value={activeCount} />
        <TinyStat label="Done" value={summary.finished} />
        <TinyStat label="Queue" value={summary.queued} />
        <TinyStat label="Block" value={summary.blocked} />
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-zinc-500">
        <span className="rounded bg-zinc-100 px-2 py-1">Depth {depth}</span>
        <span className="rounded bg-zinc-100 px-2 py-1">{summary.total} ops</span>
        {node.assignment_status ? <span className="rounded bg-zinc-100 px-2 py-1">{node.assignment_status}</span> : null}
      </div>
    </div>
  );
}

function LegendItem({ label, className }: { label: string; className: string }) {
  return (
    <span className="inline-flex items-center gap-2 rounded border border-zinc-200 bg-white px-2 py-1 text-zinc-600">
      <span className={`h-2.5 w-2.5 rounded-full ${className}`} />
      {label}
    </span>
  );
}

function TinyStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded bg-zinc-50 p-2">
      <div className="text-zinc-500">{label}</div>
      <div className="mt-1 font-semibold text-zinc-900">{value}</div>
    </div>
  );
}

function TreeMetric({ label, value, subLabel }: { label: string; value: string | number; subLabel: string }) {
  return (
    <div className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
      <div className="text-sm text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-zinc-500">{subLabel}</div>
    </div>
  );
}

function productTreePath(scenarioId: number | null, rootOrderId: string, rootLimit: number) {
  const params = new URLSearchParams({
    root_limit: String(rootLimit),
    max_depth: '8'
  });
  if (rootOrderId.trim()) {
    params.set('root_order_id', rootOrderId.trim());
  }
  return `/scenarios/${scenarioId}/product-tree?${params.toString()}`;
}

function summarizeTree(roots: ProductTreeNode[]) {
  const totals = { orders: 0, running: 0, finished: 0, blocked: 0 };
  const visit = (node: ProductTreeNode) => {
    totals.orders += 1;
    if (node.computed_status === 'Running') {
      totals.running += 1;
    }
    if (node.computed_status === 'Finished') {
      totals.finished += 1;
    }
    if (node.computed_status === 'Blocked') {
      totals.blocked += 1;
    }
    node.children.forEach(visit);
  };
  roots.forEach(visit);
  return totals;
}

function statusBorder(status: string) {
  if (status === 'Running') {
    return 'border-blue-300';
  }
  if (status === 'Finished') {
    return 'border-emerald-300';
  }
  if (status === 'Blocked') {
    return 'border-red-300';
  }
  return 'border-zinc-200';
}

function statusDot(status: string) {
  if (status === 'Running') {
    return 'bg-blue-600';
  }
  if (status === 'Finished') {
    return 'bg-emerald-600';
  }
  if (status === 'Blocked') {
    return 'bg-red-600';
  }
  if (status === 'Queued') {
    return 'bg-amber-500';
  }
  return 'bg-zinc-400';
}

function progressColor(status: string) {
  if (status === 'Running') {
    return 'bg-blue-600';
  }
  if (status === 'Finished') {
    return 'bg-emerald-600';
  }
  if (status === 'Blocked') {
    return 'bg-red-600';
  }
  return 'bg-zinc-400';
}
