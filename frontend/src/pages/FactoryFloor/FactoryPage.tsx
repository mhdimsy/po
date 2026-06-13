import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import { apiGet, apiPost } from '../../api/client';
import { LoadingButton } from '../../components/LoadingButton';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type {
  CurrentMachineState,
  CurrentOperationState,
  FactoryEvent,
  ManagerDashboard,
  OptimizationRun,
  Scenario,
  ScheduleOperation,
  SimulationRun,
  SimulationStepResponse
} from '../../types/api';

type MachineFilter = 'all' | 'idle' | 'queued' | 'running' | 'bottleneck';
type OperationFilter = 'active' | 'running' | 'setup' | 'queued' | 'blocked' | 'finished';

export function FactoryPage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [machineFilter, setMachineFilter] = useState<MachineFilter>('all');
  const [operationFilter, setOperationFilter] = useState<OperationFilter>('active');
  const [autoRun, setAutoRun] = useState(false);
  const [stepMinutes, setStepMinutes] = useState(15);
  const [tickSeconds, setTickSeconds] = useState(2);
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios'), refetchInterval: 5000 });
  const dashboard = useQuery({
    queryKey: ['factory-dashboard', scenarioId],
    queryFn: () => apiGet<ManagerDashboard>(scenarioId ? `/dashboard/manager?scenario_id=${scenarioId}` : '/dashboard/manager'),
    refetchInterval: 5000
  });
  const machines = useQuery({ queryKey: ['current-machines'], queryFn: () => apiGet<CurrentMachineState[]>('/events/current/machines?limit=1000'), refetchInterval: 5000 });
  const operations = useQuery({ queryKey: ['current-operations'], queryFn: () => apiGet<CurrentOperationState[]>('/events/current/operations?limit=1000'), refetchInterval: 5000 });
  const runs = useQuery({
    queryKey: ['factory-runs', scenarioId],
    queryFn: () => apiGet<OptimizationRun[]>(`/optimizer/runs?scenario_id=${scenarioId}`),
    enabled: scenarioId !== null,
    refetchInterval: 5000
  });
  const simulationRuns = useQuery({
    queryKey: ['simulation-runs', scenarioId],
    queryFn: () => apiGet<SimulationRun[]>(`/simulations/${scenarioId}/runs`),
    enabled: scenarioId !== null,
    refetchInterval: 5000
  });
  const events = useQuery({
    queryKey: ['factory-events', scenarioId],
    queryFn: () => apiGet<FactoryEvent[]>(`/events?scenario_id=${scenarioId}&limit=80`),
    enabled: scenarioId !== null,
    refetchInterval: autoRun ? 1500 : 5000
  });
  const latestRunId = runs.data?.[0]?.id ?? null;
  const latestSimulation = simulationRuns.data?.[0] ?? null;
  const schedule = useQuery({
    queryKey: ['factory-schedule', latestRunId],
    queryFn: () => apiGet<ScheduleOperation[]>(`/optimizer/runs/${latestRunId}/schedule`),
    enabled: latestRunId !== null,
    refetchInterval: 5000
  });
  const refreshFactory = () => {
    dashboard.refetch();
    machines.refetch();
    operations.refetch();
    runs.refetch();
    simulationRuns.refetch();
    schedule.refetch();
  };
  const runOptimizer = useMutation({
    mutationFn: () => apiPost('/optimizer/run', { scenario_id: scenarioId }),
    onSuccess: refreshFactory
  });
  const acceptProgram = useMutation({
    mutationFn: () => apiPost(`/optimizer/runs/${latestRunId}/accept`),
    onSuccess: refreshFactory
  });
  const startSimulation = useMutation({
    mutationFn: () => apiPost<SimulationRun>(`/simulations/${scenarioId}/start`, { speed_factor: 1, start_time: latestSimulation?.current_sim_time ?? 0 }),
    onSuccess: refreshFactory
  });
  const stepSimulation = useMutation({
    mutationFn: (minutes: number) => apiPost<SimulationStepResponse>(`/simulations/${scenarioId}/step`, {
      minutes,
      process_one_operation: true,
      max_operation_transitions: Math.min(500, Math.max(1, minutes))
    }),
    onSuccess: refreshFactory
  });

  useEffect(() => {
    if (!autoRun || !scenarioId || !latestSimulation || stepSimulation.isPending) {
      return;
    }
    const handle = window.setInterval(() => {
      if (!stepSimulation.isPending) {
        stepSimulation.mutate(stepMinutes);
      }
    }, Math.max(1, tickSeconds) * 1000);
    return () => window.clearInterval(handle);
  }, [autoRun, latestSimulation, scenarioId, stepMinutes, stepSimulation.isPending, stepSimulation.mutate, tickSeconds]);

  useEffect(() => {
    if (scenarioId === null && scenarios.data?.[0]?.id) {
      setScenarioId(scenarios.data[0].id);
    }
  }, [scenarioId, scenarios.data]);

  const scenarioMachines = useMemo(
    () => (machines.data ?? []).filter((machine) => scenarioId === null || machine.scenario_id === scenarioId),
    [machines.data, scenarioId]
  );
  const scenarioOperations = useMemo(
    () => (operations.data ?? []).filter((operation) => scenarioId === null || operation.scenario_id === scenarioId),
    [operations.data, scenarioId]
  );
  const operationsByMachine = useMemo(() => groupOperationsByMachine(scenarioOperations), [scenarioOperations]);
  const filteredMachines = useMemo(
    () => scenarioMachines.filter((machine) => machineMatchesFilter(machine, operationsByMachine.get(machine.machine_id) ?? [], machineFilter)),
    [machineFilter, operationsByMachine, scenarioMachines]
  );
  const visibleMachines = filteredMachines.slice(0, 72);
  const filteredOperations = useMemo(
    () => scenarioOperations.filter((operation) => operationMatchesFilter(operation, operationFilter)).slice(0, 120),
    [operationFilter, scenarioOperations]
  );
  const runningOperations = scenarioOperations.filter((operation) => ['Running', 'Setup', 'QC', 'Rework'].includes(operation.status));
  const visibleSchedule = (schedule.data ?? []).slice(0, 120);
  const latestSchedule = schedule.data ?? [];
  const maxBottleneck = Math.max(1, ...(dashboard.data?.bottleneck.map((item) => item.queued_operations) ?? [1]));

  return (
    <Page
      title="Factory"
      eyebrow="Live factory view"
      actions={
        <>
          <select
            className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm"
            value={scenarioId ?? ''}
            onChange={(event) => setScenarioId(event.target.value ? Number(event.target.value) : null)}
          >
            <option value="">All scenarios</option>
            {scenarios.data?.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
          <LoadingButton
            className="h-9 px-4"
            disabled={!scenarioId || runOptimizer.isPending}
            loading={runOptimizer.isPending}
            onClick={() => runOptimizer.mutate()}
          >
            Build program
          </LoadingButton>
          <LoadingButton
            className="h-9 px-4"
            variant="secondary"
            disabled={!latestRunId || acceptProgram.isPending}
            loading={acceptProgram.isPending}
            onClick={() => acceptProgram.mutate()}
          >
            Apply program
          </LoadingButton>
        </>
      }
    >
      {dashboard.error ? <ErrorState error={dashboard.error} /> : null}
      {machines.error ? <ErrorState error={machines.error} /> : null}
      {operations.error ? <ErrorState error={operations.error} /> : null}
      {runOptimizer.error ? <ErrorState error={runOptimizer.error} /> : null}
      {acceptProgram.error ? <ErrorState error={acceptProgram.error} /> : null}
      {startSimulation.error ? <ErrorState error={startSimulation.error} /> : null}
      {stepSimulation.error ? <ErrorState error={stepSimulation.error} /> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <FactoryMetric label="Orders" value={dashboard.data?.delivery.total_orders ?? 0} subLabel={`${dashboard.data?.delivery.on_time_rate_percent ?? 0}% on-time`} tone="teal" />
        <FactoryMetric label="Operations" value={dashboard.data?.production_progress.total_operations ?? 0} subLabel={`${dashboard.data?.production_progress.completion_percent ?? 0}% complete`} tone="blue" />
        <FactoryMetric label="Queued" value={dashboard.data?.production_progress.queued_operations ?? 0} subLabel={`${dashboard.data?.delay.delayed_operations ?? 0} delayed`} tone="amber" />
        <FactoryMetric label="Machines" value={dashboard.data?.capacity.total_machines ?? 0} subLabel={`${dashboard.data?.capacity.machine_utilization_percent ?? 0}% utilized`} tone="zinc" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(26rem,0.55fr)]">
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-base font-semibold">Simulation control</h2>
              <div className="mt-1 text-sm text-zinc-500">
                Current time: {latestSimulation?.current_sim_time ?? 0} min · Status: {latestSimulation?.status ?? 'Not started'}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <LoadingButton disabled={!scenarioId} loading={startSimulation.isPending} onClick={() => startSimulation.mutate()}>
                Start
              </LoadingButton>
              <LoadingButton variant={autoRun ? 'danger' : 'secondary'} disabled={!scenarioId || !latestSimulation} onClick={() => setAutoRun((value) => !value)}>
                {autoRun ? 'Stop auto run' : 'Auto run'}
              </LoadingButton>
              <LoadingButton variant="secondary" disabled={!scenarioId || !latestSimulation || autoRun} loading={stepSimulation.isPending} onClick={() => stepSimulation.mutate(stepMinutes)}>
                Step {stepMinutes} min
              </LoadingButton>
            </div>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="grid gap-1 text-sm">
              <span className="text-zinc-600">Simulation minutes per tick</span>
              <input
                className="h-9 rounded border border-zinc-300 px-2"
                min={1}
                max={500}
                type="number"
                value={stepMinutes}
                onChange={(event) => setStepMinutes(Number(event.target.value))}
              />
            </label>
            <label className="grid gap-1 text-sm">
              <span className="text-zinc-600">Real seconds per tick</span>
              <input
                className="h-9 rounded border border-zinc-300 px-2"
                min={1}
                max={60}
                type="number"
                value={tickSeconds}
                onChange={(event) => setTickSeconds(Number(event.target.value))}
              />
            </label>
          </div>
          <div className="mt-3 rounded border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-700">
            Scale: every {tickSeconds}s in the real world advances {stepMinutes} simulation minutes.
            {autoRun ? <span className="ml-2 font-medium text-teal-700">Auto run is active.</span> : null}
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-4">
            <MiniStat label="Running" value={countByStatus(scenarioOperations, ['Running'])} />
            <MiniStat label="Setup" value={countByStatus(scenarioOperations, ['Setup'])} />
            <MiniStat label="Queued" value={countByStatus(scenarioOperations, ['Queued'])} />
            <MiniStat label="Blocked" value={countByStatus(scenarioOperations, ['Blocked', 'BlockedByNCR', 'WaitingMaterial', 'WaitingMachine'])} />
          </div>
          {stepSimulation.data?.operation_transition ? (
            <div className="mt-4 rounded border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
              Last transition: {stepSimulation.data.operation_transition.operation_id} · M {stepSimulation.data.operation_transition.machine_id ?? '-'} · {stepSimulation.data.operation_transition.previous_status} → {stepSimulation.data.operation_transition.next_status}
            </div>
          ) : null}
        </div>

        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold">Now working</h2>
          <div className="mt-3 space-y-2">
            {runningOperations.length ? runningOperations.slice(0, 8).map((operation) => (
              <OperationRow key={operation.id} operation={operation} />
            )) : <EmptyState label="No operation is running yet. Use Start and Step." />}
          </div>
        </div>
      </section>

      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-base font-semibold">Factory events</h2>
            <div className="mt-1 text-sm text-zinc-500">Live event feed for starts, setup, finishes, schedule and simulation ticks.</div>
          </div>
          <Status value={events.isFetching ? 'Refreshing' : `${events.data?.length ?? 0} events`} />
        </div>
        {events.data?.length ? (
          <div className="grid gap-2 xl:grid-cols-2">
            {events.data.slice(0, 24).map((event) => (
              <div key={event.event_id} className="rounded border border-zinc-200 p-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-medium">{formatFactoryEvent(event)}</div>
                  <Status value={event.event_type} />
                </div>
                <div className="mt-1 text-xs text-zinc-500">
                  t={event.simulation_time ?? '-'} · {event.aggregate_type} {event.aggregate_id} · {new Date(event.created_at).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        ) : <EmptyState label="No events yet. Start simulation or build/apply a program." />}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[minmax(0,1.55fr)_minmax(24rem,0.75fr)]">
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h2 className="text-base font-semibold">Factory floor</h2>
              <div className="mt-1 text-sm text-zinc-500">{visibleMachines.length} machine cells shown · filter: {machineFilter}</div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Segmented
                value={machineFilter}
                options={[
                  ['all', 'All'],
                  ['idle', 'Idle'],
                  ['queued', 'Has work'],
                  ['running', 'Running'],
                  ['bottleneck', 'Bottleneck']
                ]}
                onChange={(value) => setMachineFilter(value as MachineFilter)}
              />
              <Status value={`${scenarioOperations.length} operations`} />
              <Status value={machines.isFetching || operations.isFetching ? 'Refreshing' : 'Live'} />
            </div>
          </div>
          {visibleMachines.length ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              {visibleMachines.map((machine) => {
                const queue = operationsByMachine.get(machine.machine_id) ?? [];
                const active = queue.find((operation) => operation.status === 'Running') ?? queue[0];
                const queuePercent = Math.min(100, queue.length * 8);
                return (
                  <div key={machine.id} className="rounded border border-zinc-200 bg-zinc-50 p-3 transition hover:-translate-y-0.5 hover:border-teal-300 hover:shadow-md">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">Machine {machine.machine_id}</div>
                      <span className={`h-3 w-3 rounded-full ${statusDot(machine.status)} ${machine.status === 'Available' ? 'status-pulse' : ''}`} />
                    </div>
                    <div className="mt-1 text-xs text-zinc-500">{String(machine.payload_json.title ?? 'Production cell')}</div>
                    <div className="mt-3 h-2 overflow-hidden rounded bg-zinc-200">
                      <div className="bar-grow h-full rounded bg-teal-600" style={{ width: `${queuePercent}%` }} />
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                      <div className="rounded bg-white p-2">
                        <div className="text-zinc-500">Queue</div>
                        <div className="mt-1 font-semibold">{queue.length}</div>
                      </div>
                      <div className="rounded bg-white p-2">
                        <div className="text-zinc-500">Status</div>
                        <div className="mt-1 font-semibold">{queue.length ? 'Has work' : machine.status}</div>
                      </div>
                    </div>
                    <div className="mt-3 truncate rounded border border-zinc-200 bg-white px-2 py-1 text-xs">
                      {active ? `${active.operation_id} · ${active.status}` : 'No queued operation'}
                    </div>
                    {queue.length > 8 ? (
                      <div className="mt-2 rounded bg-amber-100 px-2 py-1 text-xs font-medium text-amber-900">
                        Bottleneck pressure
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState label="Initialize a scenario to see machines and operations." />
          )}
        </div>

        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Bottlenecks</h2>
            <Status value={`${dashboard.data?.bottleneck.length ?? 0} active`} />
          </div>
          <div className="mt-4 space-y-3 text-sm">
            {dashboard.data?.bottleneck.length ? dashboard.data.bottleneck.map((item) => (
              <div key={item.resource_id} className="rounded border border-zinc-200 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-medium">Machine {item.resource_id}</span>
                  <span className="text-zinc-500">{item.queued_operations} queued</span>
                </div>
                <div className="h-2 overflow-hidden rounded bg-zinc-100">
                  <div
                    className="bar-grow h-full rounded bg-amber-500"
                    style={{ width: `${Math.max(6, (item.queued_operations / maxBottleneck) * 100)}%` }}
                  />
                </div>
              </div>
            )) : <EmptyState label="No bottlenecks yet." />}
          </div>
        </div>
      </section>

      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h2 className="text-base font-semibold">Operations board</h2>
            <div className="mt-1 text-sm text-zinc-500">Shows who is assigned, which machine is used, and current operation state.</div>
          </div>
          <Segmented
            value={operationFilter}
            options={[
              ['active', 'Active'],
              ['running', 'Running'],
              ['setup', 'Setup'],
              ['queued', 'Queued'],
              ['blocked', 'Blocked'],
              ['finished', 'Finished']
            ]}
            onChange={(value) => setOperationFilter(value as OperationFilter)}
          />
        </div>
        {filteredOperations.length ? (
          <div className="overflow-auto">
            <table className="w-full min-w-[860px] text-left text-sm">
              <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500">
                <tr>
                  <th className="p-3">Operation</th>
                  <th className="p-3">Order</th>
                  <th className="p-3">Machine</th>
                  <th className="p-3">Operator</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Duration</th>
                </tr>
              </thead>
              <tbody>
                {filteredOperations.map((operation) => (
                  <tr key={operation.id} className="border-t border-zinc-200">
                    <td className="p-3 font-medium">{operation.operation_id}</td>
                    <td className="p-3">{operation.order_id ?? '-'}</td>
                    <td className="p-3">M {operation.machine_id ?? 'Unassigned'}</td>
                    <td className="p-3">{operation.operator_id ?? 'Unassigned'}</td>
                    <td className="p-3"><Status value={operation.status} /></td>
                    <td className="p-3">{String(operation.payload_json.duration ?? operation.payload_json.operation_duration ?? '-')} min</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <EmptyState label="No operations match this filter." />}
      </section>

      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold">Program timeline</h2>
            <div className="mt-1 text-sm text-zinc-500">{latestSchedule.length} scheduled operations</div>
          </div>
          <div className="flex gap-2">
            <Status value={latestRunId ? `Run ${latestRunId}` : 'No program'} />
            <Status value={schedule.isFetching ? 'Refreshing' : 'Idle'} />
          </div>
        </div>
        {visibleSchedule.length ? (
          <div className="space-y-2 overflow-auto">
            {visibleSchedule.map((item) => (
              <div key={item.id} className="grid min-w-[680px] grid-cols-[9rem_1fr_5rem] items-center gap-3 text-sm">
                <div className="truncate text-zinc-600">M {item.machine_id ?? '-'}</div>
                <div className="relative h-8 rounded bg-zinc-100">
                  <div
                    className={`bar-grow absolute top-1 h-6 rounded ${item.status === 'Blocked' ? 'bg-red-600' : item.status === 'Accepted' ? 'bg-emerald-600' : 'bg-blue-600'}`}
                    style={{
                      left: `${Math.min(94, (item.start_time % 1440) / 14.4)}%`,
                      width: `${Math.max(2, Math.min(40, (item.end_time - item.start_time) / 14.4))}%`
                    }}
                  />
                  <div className="absolute inset-0 flex items-center px-2 text-xs font-medium text-zinc-800">
                    {item.operation_id}
                  </div>
                </div>
                <Status value={item.status} />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState label="Use Build program to generate a visible schedule." />
        )}
      </section>
    </Page>
  );
}

function FactoryMetric({ label, value, subLabel, tone }: { label: string; value: string | number; subLabel: string; tone: 'teal' | 'blue' | 'amber' | 'zinc' }) {
  const toneClass = {
    teal: 'bg-teal-50 text-teal-800 border-teal-200',
    blue: 'bg-blue-50 text-blue-800 border-blue-200',
    amber: 'bg-amber-50 text-amber-900 border-amber-200',
    zinc: 'bg-zinc-50 text-zinc-800 border-zinc-200'
  }[tone];
  return (
    <div className={`rounded border p-5 shadow-sm ${toneClass}`}>
      <div className="text-sm text-zinc-500">{label}</div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
      <div className="mt-2 text-sm">{subLabel}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-zinc-200 bg-zinc-50 p-3">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}

function OperationRow({ operation }: { operation: CurrentOperationState }) {
  return (
    <div className="rounded border border-zinc-200 p-3 text-sm">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate font-medium">{operation.operation_id}</div>
          <div className="mt-1 truncate text-xs text-zinc-500">Order {operation.order_id ?? '-'} · M {operation.machine_id ?? 'Unassigned'}</div>
        </div>
        <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${operation.status === 'Running' ? 'bg-blue-500 status-pulse' : 'bg-amber-500'}`} />
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
        <div className="rounded bg-zinc-50 p-2">
          <div className="text-zinc-500">Operator</div>
          <div className="mt-1 font-medium">{operation.operator_id ?? 'Unassigned'}</div>
        </div>
        <div className="rounded bg-zinc-50 p-2">
          <div className="text-zinc-500">Status</div>
          <div className="mt-1 font-medium">{operation.status}</div>
        </div>
      </div>
    </div>
  );
}

function Segmented({ value, options, onChange }: { value: string; options: Array<[string, string]>; onChange: (value: string) => void }) {
  return (
    <div className="flex flex-wrap gap-1 rounded border border-zinc-200 bg-zinc-50 p-1">
      {options.map(([id, label]) => (
        <button
          key={id}
          className={`min-h-7 rounded px-2 py-1 text-xs font-medium transition ${value === id ? 'bg-zinc-900 text-white' : 'text-zinc-600 hover:bg-white'}`}
          type="button"
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function groupOperationsByMachine(operations: CurrentOperationState[]) {
  const groups = new Map<string, CurrentOperationState[]>();
  for (const operation of operations) {
    const key = operation.machine_id ?? 'Unassigned';
    groups.set(key, [...(groups.get(key) ?? []), operation]);
  }
  return groups;
}

function countByStatus(operations: CurrentOperationState[], statuses: string[]) {
  return operations.filter((operation) => statuses.includes(operation.status)).length;
}

function machineMatchesFilter(machine: CurrentMachineState, queue: CurrentOperationState[], filter: MachineFilter) {
  if (filter === 'all') {
    return true;
  }
  if (filter === 'idle') {
    return queue.length === 0 && ['Available', 'Idle', 'Reserved'].includes(machine.status);
  }
  if (filter === 'queued') {
    return queue.length > 0;
  }
  if (filter === 'running') {
    return queue.some((operation) => ['Running', 'Setup'].includes(operation.status));
  }
  if (filter === 'bottleneck') {
    return queue.length > 8;
  }
  return true;
}

function operationMatchesFilter(operation: CurrentOperationState, filter: OperationFilter) {
  if (filter === 'active') {
    return !['Finished', 'Completed'].includes(operation.status);
  }
  if (filter === 'running') {
    return operation.status === 'Running';
  }
  if (filter === 'setup') {
    return operation.status === 'Setup';
  }
  if (filter === 'queued') {
    return ['Queued', 'WaitingMaterial', 'WaitingMachine', 'WaitingOperator', 'WaitingQCApproval'].includes(operation.status);
  }
  if (filter === 'blocked') {
    return ['Blocked', 'BlockedByNCR', 'WaitingMaterial', 'WaitingMachine'].includes(operation.status);
  }
  if (filter === 'finished') {
    return ['Finished', 'Completed'].includes(operation.status);
  }
  return true;
}

function statusDot(status: string) {
  if (status === 'Available' || status === 'Idle') {
    return 'bg-emerald-500';
  }
  if (status === 'Failure' || status === 'Offline') {
    return 'bg-red-500';
  }
  if (status === 'Busy' || status === 'Running') {
    return 'bg-blue-500';
  }
  return 'bg-amber-500';
}

function formatFactoryEvent(event: FactoryEvent) {
  const payload = event.payload_json ?? {};
  const machine = typeof payload.machine_id === 'string' ? ` on machine ${payload.machine_id}` : '';
  const operator = typeof payload.operator_id === 'string' ? ` by ${payload.operator_id}` : '';
  const order = typeof payload.order_id === 'string' ? ` for order ${payload.order_id}` : '';
  if (event.event_type === 'OperationStarted') {
    return `Operation ${event.aggregate_id} started${machine}${operator}${order}`;
  }
  if (event.event_type === 'OperationSetup') {
    return `Operation ${event.aggregate_id} entered setup${machine}${operator}${order}`;
  }
  if (event.event_type === 'OperationFinished') {
    return `Operation ${event.aggregate_id} finished${machine}${operator}${order}`;
  }
  if (event.event_type === 'OperationScheduled') {
    return `Operation ${event.aggregate_id} scheduled${machine}${operator}${order}`;
  }
  if (event.event_type === 'SimulationStepped') {
    const currentTime = typeof payload.current_sim_time === 'number' ? payload.current_sim_time : event.simulation_time ?? '-';
    return `Simulation advanced to minute ${currentTime}`;
  }
  if (event.event_type === 'ScheduleSuggested') {
    const operationCount = typeof payload.operation_count === 'number' ? payload.operation_count : '-';
    return `New program suggested with ${operationCount} operations`;
  }
  if (event.event_type === 'ScheduleAccepted') {
    const acceptedOperations = typeof payload.accepted_operations === 'number' ? payload.accepted_operations : '-';
    return `Program accepted with ${acceptedOperations} operations`;
  }
  return `${event.event_type}: ${event.aggregate_type} ${event.aggregate_id}`;
}
