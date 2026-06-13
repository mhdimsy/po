import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { apiGet } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { CurrentOperationState, OptimizationRun, ProductTreeNode, ProductTreeResponse, Scenario, ScheduleOperation } from '../../types/api';

type OrderDetail = {
  orders: ProductTreeNode[];
  runningOperations: CurrentOperationState[];
  plannedOperations: ScheduleOperation[];
};

export function ProductTreePage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [rootOrderId, setRootOrderId] = useState('');
  const [rootLimit, setRootLimit] = useState(10);
  const [refreshSeconds, setRefreshSeconds] = useState(5);
  const [zoom, setZoom] = useState(0.9);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const refetchInterval = Math.max(1, refreshSeconds) * 1000;

  const scenarios = useQuery({ queryKey: ['tree-scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios'), refetchInterval });
  const activeScenarioId = scenarioId ?? scenarios.data?.[0]?.id ?? null;
  const tree = useQuery({
    queryKey: ['product-tree', activeScenarioId, rootOrderId, rootLimit],
    queryFn: () => apiGet<ProductTreeResponse>(productTreePath(activeScenarioId, rootOrderId, rootLimit)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const operations = useQuery({
    queryKey: ['tree-current-operations', activeScenarioId],
    queryFn: () => apiGet<CurrentOperationState[]>(currentStatePath('/events/current/operations', activeScenarioId, 10000)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const runs = useQuery({
    queryKey: ['tree-optimizer-runs', activeScenarioId],
    queryFn: () => apiGet<OptimizationRun[]>(`/optimizer/runs?scenario_id=${activeScenarioId}`),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const latestRunId = runs.data?.[0]?.id ?? null;
  const schedule = useQuery({
    queryKey: ['tree-schedule', latestRunId],
    queryFn: () => apiGet<ScheduleOperation[]>(`/optimizer/runs/${latestRunId}/schedule`),
    enabled: latestRunId !== null,
    refetchInterval
  });
  const totals = useMemo(() => summarizeTree(tree.data?.roots ?? []), [tree.data]);
  const selectedNode = useMemo(() => findNode(tree.data?.roots ?? [], selectedOrderId), [selectedOrderId, tree.data]);
  const detail = useMemo(
    () => buildOrderDetail(selectedNode, operations.data ?? [], schedule.data ?? []),
    [operations.data, schedule.data, selectedNode]
  );

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
      {operations.error ? <ErrorState error={operations.error} /> : null}
      {runs.error ? <ErrorState error={runs.error} /> : null}
      {schedule.error ? <ErrorState error={schedule.error} /> : null}

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
                <TreeNodeView key={root.order_id} node={root} depth={0} selectedOrderId={selectedOrderId} onSelect={setSelectedOrderId} />
              ))}
            </div>
          </div>
        ) : (
          <EmptyState label="No product tree found for this scenario/order. Try another order id or rebuild the demo database." />
        )}
      </section>

      <OrderDetailPanel detail={detail} node={selectedNode} onClose={() => setSelectedOrderId(null)} />
    </Page>
  );
}

function TreeNodeView({ node, depth, selectedOrderId, onSelect }: { node: ProductTreeNode; depth: number; selectedOrderId: string | null; onSelect: (orderId: string) => void }) {
  return (
    <div className="tree-row flex items-start">
      <OrderNodeCard depth={depth} isSelected={selectedOrderId === node.order_id} node={node} onSelect={onSelect} />
      {node.children.length ? (
        <div className="tree-children relative flex flex-col gap-4 pl-12">
          {node.children.map((child) => (
            <div key={child.order_id} className="tree-child relative">
              <TreeNodeView node={child} depth={depth + 1} selectedOrderId={selectedOrderId} onSelect={onSelect} />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function OrderNodeCard({ node, depth, isSelected, onSelect }: { node: ProductTreeNode; depth: number; isSelected: boolean; onSelect: (orderId: string) => void }) {
  const summary = node.operation_summary;
  const progress = summary.total ? Math.round((summary.finished / summary.total) * 100) : 0;
  const activeCount = summary.running + summary.setup;
  return (
    <button
      className={`tree-node w-80 shrink-0 rounded border bg-white p-4 text-left shadow-sm ${statusBorder(node.computed_status)} ${isSelected ? 'ring-2 ring-teal-600' : ''}`}
      type="button"
      onClick={() => onSelect(node.order_id)}
    >
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
    </button>
  );
}

function OrderDetailPanel({ detail, node, onClose }: { detail: OrderDetail | null; node: ProductTreeNode | null; onClose: () => void }) {
  if (!node || !detail) {
    return (
      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <EmptyState label="Select an order node to see child orders and running/planned operations." />
      </section>
    );
  }
  return (
    <section className="grid gap-4 xl:grid-cols-[minmax(22rem,0.7fr)_minmax(0,1.3fr)]">
      <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs font-medium uppercase tracking-normal text-teal-700">Selected order</div>
            <h2 className="mt-1 text-lg font-semibold">Order {node.order_id}</h2>
            <div className="mt-1 text-sm text-zinc-500">{node.order_code ?? node.product_code ?? 'No code'}</div>
          </div>
          <button className="rounded border border-zinc-300 px-2 py-1 text-xs text-zinc-600 hover:bg-zinc-50" type="button" onClick={onClose}>Close</button>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          <DetailStat label="Status" value={node.computed_status} />
          <DetailStat label="Subtree orders" value={detail.orders.length} />
          <DetailStat label="Running ops" value={detail.runningOperations.length} />
          <DetailStat label="Planned ops" value={detail.plannedOperations.length} />
        </div>
        <div className="mt-4">
          <h3 className="text-sm font-semibold">Orders in this branch</h3>
          <div className="mt-2 max-h-80 space-y-2 overflow-auto pr-1">
            {detail.orders.map((order) => (
              <div key={order.order_id} className="rounded border border-zinc-200 p-2 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{order.order_id}</span>
                  <Status value={order.computed_status} />
                </div>
                <div className="mt-1 truncate text-xs text-zinc-500">{order.order_code ?? order.product_code ?? '-'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-2">
          <OperationList title="Running now" operations={detail.runningOperations} emptyLabel="No operation in this branch is currently running." />
          <ScheduleList title="Planned next" schedule={detail.plannedOperations} emptyLabel="No planned operation found for this branch." />
        </div>
      </div>
    </section>
  );
}

function DetailStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-zinc-200 bg-zinc-50 p-3">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 font-semibold">{value}</div>
    </div>
  );
}

function OperationList({ title, operations, emptyLabel }: { title: string; operations: CurrentOperationState[]; emptyLabel: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-3 max-h-[30rem] space-y-2 overflow-auto pr-1">
        {operations.length ? operations.map((operation) => (
          <div key={operation.id} className="rounded border border-zinc-200 p-3 text-sm">
            <div className="flex items-center justify-between gap-2">
              <span className="truncate font-medium">{operation.operation_id}</span>
              <Status value={operation.status} />
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
              <DetailCell label="Order" value={operation.order_id ?? '-'} />
              <DetailCell label="Machine" value={operation.machine_id ?? '-'} />
              <DetailCell label="Operator" value={operation.operator_id ?? '-'} />
              <DetailCell label="Duration" value={`${String(operation.payload_json.duration ?? operation.payload_json.operation_duration ?? '-')}m`} />
            </div>
          </div>
        )) : <EmptyState label={emptyLabel} />}
      </div>
    </div>
  );
}

function ScheduleList({ title, schedule, emptyLabel }: { title: string; schedule: ScheduleOperation[]; emptyLabel: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-3 max-h-[30rem] space-y-2 overflow-auto pr-1">
        {schedule.length ? schedule.map((item) => (
          <div key={item.id} className="rounded border border-zinc-200 p-3 text-sm">
            <div className="flex items-center justify-between gap-2">
              <span className="truncate font-medium">{item.operation_id}</span>
              <Status value={item.status} />
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
              <DetailCell label="Order" value={item.order_id ?? '-'} />
              <DetailCell label="Machine" value={item.machine_id ?? '-'} />
              <DetailCell label="Operator" value={item.operator_id ?? '-'} />
              <DetailCell label="Window" value={`${item.start_time} -> ${item.end_time}`} />
            </div>
          </div>
        )) : <EmptyState label={emptyLabel} />}
      </div>
    </div>
  );
}

function DetailCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded bg-zinc-50 p-2">
      <div className="text-zinc-500">{label}</div>
      <div className="mt-1 truncate font-medium text-zinc-900">{value}</div>
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

function currentStatePath(path: string, scenarioId: number | null, limit: number) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (scenarioId !== null) {
    params.set('scenario_id', String(scenarioId));
  }
  return `${path}?${params.toString()}`;
}

function findNode(roots: ProductTreeNode[], orderId: string | null): ProductTreeNode | null {
  if (!orderId) {
    return null;
  }
  for (const root of roots) {
    const found = findNodeRecursive(root, orderId);
    if (found) {
      return found;
    }
  }
  return null;
}

function findNodeRecursive(node: ProductTreeNode, orderId: string): ProductTreeNode | null {
  if (node.order_id === orderId) {
    return node;
  }
  for (const child of node.children) {
    const found = findNodeRecursive(child, orderId);
    if (found) {
      return found;
    }
  }
  return null;
}

function buildOrderDetail(node: ProductTreeNode | null, operations: CurrentOperationState[], schedule: ScheduleOperation[]): OrderDetail | null {
  if (!node) {
    return null;
  }
  const orders = flattenOrders(node);
  const orderIds = new Set(orders.map((order) => order.order_id));
  const runningOperations = operations
    .filter((operation) => operation.order_id !== null && orderIds.has(operation.order_id))
    .filter((operation) => ['Running', 'Setup', 'QC', 'Rework'].includes(operation.status))
    .sort((a, b) => a.operation_id.localeCompare(b.operation_id))
    .slice(0, 80);
  const plannedOperations = schedule
    .filter((item) => item.order_id !== null && orderIds.has(item.order_id))
    .filter((item) => !runningOperations.some((operation) => operation.operation_id === item.operation_id))
    .sort((a, b) => a.start_time - b.start_time)
    .slice(0, 120);
  return { orders, runningOperations, plannedOperations };
}

function flattenOrders(root: ProductTreeNode): ProductTreeNode[] {
  const orders = [root];
  for (const child of root.children) {
    orders.push(...flattenOrders(child));
  }
  return orders;
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
