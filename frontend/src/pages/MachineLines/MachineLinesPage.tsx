import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { apiGet } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { CurrentMachineState, CurrentOperationState, OptimizationRun, Scenario, ScheduleOperation, SimulationRun } from '../../types/api';

type MachineViewFilter = 'active' | 'running' | 'queued' | 'all';

type MachineLine = {
  machine: CurrentMachineState;
  current: OperationSlot | null;
  upcoming: OperationSlot[];
  backlogCount: number;
};

type OperationSlot = {
  operationId: string;
  orderId: string | null;
  operatorId: string | null;
  status: string;
  actualStartTime: number | null;
  startTime: number | null;
  endTime: number | null;
  duration: number | null;
};

type OperationProgress = {
  isScheduled: boolean;
  elapsed: number;
  remaining: number;
  total: number;
  percent: number;
};

export function MachineLinesPage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [filter, setFilter] = useState<MachineViewFilter>('active');
  const [refreshSeconds, setRefreshSeconds] = useState(3);
  const refetchInterval = Math.max(1, refreshSeconds) * 1000;

  const scenarios = useQuery({ queryKey: ['line-scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios'), refetchInterval });
  const activeScenarioId = scenarioId ?? scenarios.data?.[0]?.id ?? null;
  const machines = useQuery({
    queryKey: ['line-machines', activeScenarioId],
    queryFn: () => apiGet<CurrentMachineState[]>(currentStatePath('/events/current/machines', activeScenarioId, 2000)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const operations = useQuery({
    queryKey: ['line-operations', activeScenarioId],
    queryFn: () => apiGet<CurrentOperationState[]>(currentStatePath('/events/current/operations', activeScenarioId, 10000)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const runs = useQuery({
    queryKey: ['line-runs', activeScenarioId],
    queryFn: () => apiGet<OptimizationRun[]>(`/optimizer/runs?scenario_id=${activeScenarioId}`),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const simulationRuns = useQuery({
    queryKey: ['line-simulation-runs', activeScenarioId],
    queryFn: () => apiGet<SimulationRun[]>(`/simulations/${activeScenarioId}/runs`),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const latestRunId = runs.data?.[0]?.id ?? null;
  const currentSimTime = simulationRuns.data?.[0]?.current_sim_time ?? 0;
  const schedule = useQuery({
    queryKey: ['line-schedule', latestRunId],
    queryFn: () => apiGet<ScheduleOperation[]>(`/optimizer/runs/${latestRunId}/schedule`),
    enabled: latestRunId !== null,
    refetchInterval
  });

  const machineLines = useMemo(
    () => buildMachineLines(machines.data ?? [], operations.data ?? [], schedule.data ?? [], activeScenarioId),
    [activeScenarioId, machines.data, operations.data, schedule.data]
  );
  const visibleLines = useMemo(() => machineLines.filter((line) => lineMatchesFilter(line, filter)).slice(0, 120), [filter, machineLines]);
  const runningCount = machineLines.filter((line) => line.current?.status === 'Running').length;
  const queuedCount = machineLines.reduce((sum, line) => sum + line.backlogCount, 0);

  return (
    <Page
      title="Machine Lines"
      eyebrow="Current work and next jobs"
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
          <select
            className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm"
            value={filter}
            onChange={(event) => setFilter(event.target.value as MachineViewFilter)}
          >
            <option value="active">Active lines</option>
            <option value="running">Running only</option>
            <option value="queued">Has next jobs</option>
            <option value="all">All machines</option>
          </select>
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Refresh</span>
            <input
              className="w-14 bg-transparent text-right outline-none"
              min={1}
              max={60}
              type="number"
              value={refreshSeconds}
              onChange={(event) => setRefreshSeconds(Number(event.target.value))}
            />
            <span className="text-zinc-500">s</span>
          </label>
        </>
      }
    >
      {machines.error ? <ErrorState error={machines.error} /> : null}
      {operations.error ? <ErrorState error={operations.error} /> : null}
      {runs.error ? <ErrorState error={runs.error} /> : null}
      {simulationRuns.error ? <ErrorState error={simulationRuns.error} /> : null}
      {schedule.error ? <ErrorState error={schedule.error} /> : null}

      <section className="grid gap-4 md:grid-cols-4">
        <LineMetric label="Visible lines" value={visibleLines.length} subLabel={`${machineLines.length} total`} />
        <LineMetric label="Running now" value={runningCount} subLabel="machines with active operation" />
        <LineMetric label="Queued next" value={queuedCount} subLabel="scheduled/queued jobs" />
        <LineMetric label="Refresh" value={`${refreshSeconds}s`} subLabel={machines.isFetching || operations.isFetching ? 'refreshing now' : 'live polling'} />
      </section>

      <section className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
        <div className="mb-4 flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-base font-semibold">Machine work lines</h2>
            <div className="mt-1 text-sm text-zinc-500">Each row shows what the machine is doing now and what is coming next.</div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Status value={activeScenarioId ? `Scenario ${activeScenarioId}` : 'No scenario'} />
            <Status value={latestRunId ? `Program ${latestRunId}` : 'No program'} />
            <Status value={`t=${currentSimTime} min`} />
            <Status value={schedule.isFetching ? 'Refreshing' : 'Live'} />
          </div>
        </div>

        {visibleLines.length ? (
          <div className="space-y-3">
            {visibleLines.map((line) => (
              <MachineLineRow key={line.machine.id} currentSimTime={currentSimTime} line={line} />
            ))}
          </div>
        ) : (
          <EmptyState label="No machine lines match this filter. Build/apply a program or start the simulation." />
        )}
      </section>
    </Page>
  );
}

function MachineLineRow({ line, currentSimTime }: { line: MachineLine; currentSimTime: number }) {
  return (
    <div className="grid gap-3 rounded border border-zinc-200 bg-zinc-50 p-3 xl:grid-cols-[15rem_minmax(0,1fr)]">
      <div className="flex min-w-0 flex-col justify-between rounded border border-zinc-200 bg-white p-3">
        <div>
          <div className="flex items-center justify-between gap-2">
            <div className="truncate font-semibold">Machine {line.machine.machine_id}</div>
            <span className={`h-3 w-3 shrink-0 rounded-full ${statusDot(line.machine.status)} ${line.current ? 'status-pulse' : ''}`} />
          </div>
          <div className="mt-1 truncate text-xs text-zinc-500">{String(line.machine.payload_json.title ?? 'Production cell')}</div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <Status value={line.machine.status} />
          <Status value={`${line.backlogCount} next`} />
        </div>
      </div>

      <div className="min-w-0 overflow-hidden rounded border border-zinc-200 bg-white p-3">
        <div className="mb-2 grid grid-cols-[minmax(13rem,0.8fr)_minmax(0,1.8fr)] gap-3 text-xs font-medium text-zinc-500">
          <div>Now</div>
          <div>Next in line</div>
        </div>
        <div className="grid min-w-[760px] grid-cols-[minmax(13rem,0.8fr)_minmax(0,1.8fr)] gap-3">
          <OperationCard currentSimTime={currentSimTime} slot={line.current} mode="current" />
          <div className={`relative overflow-hidden rounded border border-zinc-200 bg-zinc-50 p-2 ${line.upcoming.length ? 'conveyor-flow' : ''}`}>
            {line.upcoming.length ? (
              <div className="relative z-[1] flex items-stretch gap-2 overflow-x-auto pb-1">
                {line.upcoming.slice(0, 18).map((slot, index) => (
                  <OperationCard key={`${slot.operationId}-${index}`} currentSimTime={currentSimTime} slot={slot} mode="next" index={index + 1} />
                ))}
              </div>
            ) : (
              <div className="rounded border border-dashed border-zinc-300 bg-white/80 p-3 text-sm text-zinc-500">No next job assigned to this machine.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function OperationCard({ slot, mode, currentSimTime, index }: { slot: OperationSlot | null; mode: 'current' | 'next'; currentSimTime: number; index?: number }) {
  if (!slot) {
    return <div className="rounded border border-dashed border-zinc-300 bg-white p-3 text-sm text-zinc-500">Idle now</div>;
  }
  const progress = calculateProgress(slot, currentSimTime);
  return (
    <div className={`${mode === 'current' ? 'border-blue-300 bg-blue-50' : 'flex min-h-full w-40 shrink-0 flex-col border-zinc-200 bg-white'} rounded border p-3 text-sm shadow-sm`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="truncate font-semibold">{slot.operationId}</div>
          <div className="mt-1 truncate text-xs text-zinc-500">Order {slot.orderId ?? '-'}</div>
        </div>
        <Status value={mode === 'current' ? slot.status : `#${index}`} />
      </div>
      <div className={`${mode === 'next' ? 'mt-3 grid flex-1 grid-cols-1 content-start gap-2 text-xs' : 'mt-3 grid grid-cols-2 gap-2 text-xs'}`}>
        <div className="rounded bg-white/80 p-2">
          <div className="text-zinc-500">Operator</div>
          <div className="mt-1 truncate font-medium">{slot.operatorId ?? 'Unassigned'}</div>
        </div>
        <div className="rounded bg-white/80 p-2">
          <div className="text-zinc-500">Duration</div>
          <div className="mt-1 font-medium">{slot.duration ?? '-'} min</div>
        </div>
      </div>
      {mode === 'current' ? (
        <OperationProgressGauge progress={progress} />
      ) : null}
      <div className="mt-2 text-xs text-zinc-500">
        {slot.startTime !== null && slot.endTime !== null ? `plan t=${slot.startTime} -> ${slot.endTime}` : 'not scheduled'}
        {slot.actualStartTime !== null ? <span> · actual start t={slot.actualStartTime}</span> : null}
      </div>
    </div>
  );
}

function OperationProgressGauge({ progress }: { progress: OperationProgress }) {
  if (!progress.isScheduled) {
    return (
      <div className="mt-3 rounded border border-zinc-200 bg-white/80 p-2 text-xs text-zinc-500">
        Progress unavailable: this operation has no schedule window.
      </div>
    );
  }
  return (
    <div className="mt-3 rounded border border-white/80 bg-white/80 p-2">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="font-medium text-zinc-700">{progress.percent}% complete</span>
        <span className="text-zinc-500">{progress.elapsed} min passed · {progress.remaining} min left</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-zinc-200">
        <div
          className={`h-full rounded-full ${progress.remaining === 0 ? 'bg-emerald-600' : 'bg-blue-600'}`}
          style={{ width: `${progress.percent}%` }}
        />
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded bg-zinc-50 p-2">
          <div className="text-zinc-500">Elapsed</div>
          <div className="mt-1 font-semibold">{progress.elapsed}m</div>
        </div>
        <div className="rounded bg-zinc-50 p-2">
          <div className="text-zinc-500">Remaining</div>
          <div className="mt-1 font-semibold">{progress.remaining}m</div>
        </div>
        <div className="rounded bg-zinc-50 p-2">
          <div className="text-zinc-500">Total</div>
          <div className="mt-1 font-semibold">{progress.total}m</div>
        </div>
      </div>
    </div>
  );
}

function LineMetric({ label, value, subLabel }: { label: string; value: string | number; subLabel: string }) {
  return (
    <div className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
      <div className="text-sm text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-zinc-500">{subLabel}</div>
    </div>
  );
}

function buildMachineLines(
  machines: CurrentMachineState[],
  operations: CurrentOperationState[],
  schedule: ScheduleOperation[],
  scenarioId: number | null
): MachineLine[] {
  const scenarioMachines = machines.filter((machine) => scenarioId === null || machine.scenario_id === scenarioId);
  const scenarioOperations = operations.filter((operation) => scenarioId === null || operation.scenario_id === scenarioId);
  const operationsById = new Map(scenarioOperations.map((operation) => [operation.operation_id, operation]));
  const operationsByMachine = groupByMachine(scenarioOperations);
  const scheduleByMachine = groupScheduleByMachine(schedule);

  return scenarioMachines
    .map((machine) => {
      const machineOperations = operationsByMachine.get(machine.machine_id) ?? [];
      const scheduled = scheduleByMachine.get(machine.machine_id) ?? [];
      const currentOperation =
        machineOperations.find((operation) => operation.operation_id === machine.current_operation_id) ??
        machineOperations.find((operation) => ['Running', 'Setup', 'QC', 'Rework'].includes(operation.status)) ??
        null;
      const current = currentOperation ? operationToSlot(currentOperation, findSchedule(scheduled, currentOperation.operation_id)) : null;
      const upcomingFromSchedule = scheduled
        .filter((item) => item.operation_id !== current?.operationId)
        .filter((item) => !['Finished', 'Completed'].includes(operationsById.get(item.operation_id)?.status ?? ''))
        .sort((a, b) => a.start_time - b.start_time)
        .map((item) => scheduleToSlot(item, operationsById.get(item.operation_id)));
      const fallbackQueue = machineOperations
        .filter((operation) => operation.operation_id !== current?.operationId)
        .filter((operation) => ['Queued', 'WaitingMachine', 'WaitingMaterial', 'WaitingOperator', 'Setup'].includes(operation.status))
        .map((operation) => operationToSlot(operation, findSchedule(scheduled, operation.operation_id)));
      const upcoming = dedupeSlots([...upcomingFromSchedule, ...fallbackQueue]);

      return {
        machine,
        current,
        upcoming,
        backlogCount: upcoming.length
      };
    })
    .sort((a, b) => Number(Boolean(b.current)) - Number(Boolean(a.current)) || b.backlogCount - a.backlogCount || a.machine.machine_id.localeCompare(b.machine.machine_id));
}

function groupByMachine(operations: CurrentOperationState[]) {
  const groups = new Map<string, CurrentOperationState[]>();
  for (const operation of operations) {
    if (!operation.machine_id) {
      continue;
    }
    groups.set(operation.machine_id, [...(groups.get(operation.machine_id) ?? []), operation]);
  }
  return groups;
}

function groupScheduleByMachine(schedule: ScheduleOperation[]) {
  const groups = new Map<string, ScheduleOperation[]>();
  for (const item of schedule) {
    if (!item.machine_id) {
      continue;
    }
    groups.set(item.machine_id, [...(groups.get(item.machine_id) ?? []), item]);
  }
  return groups;
}

function findSchedule(schedule: ScheduleOperation[], operationId: string) {
  return schedule.find((item) => item.operation_id === operationId) ?? null;
}

function operationToSlot(operation: CurrentOperationState, schedule: ScheduleOperation | null): OperationSlot {
  const duration = readNumber(operation.payload_json.duration) ?? readNumber(operation.payload_json.operation_duration);
  return {
    operationId: operation.operation_id,
    orderId: operation.order_id,
    operatorId: operation.operator_id,
    status: operation.status,
    actualStartTime: isActiveStatus(operation.status) ? operation.simulation_time ?? null : null,
    startTime: schedule?.start_time ?? null,
    endTime: schedule?.end_time ?? null,
    duration: schedule ? schedule.end_time - schedule.start_time : duration
  };
}

function scheduleToSlot(schedule: ScheduleOperation, operation?: CurrentOperationState): OperationSlot {
  return {
    operationId: schedule.operation_id,
    orderId: operation?.order_id ?? schedule.order_id,
    operatorId: operation?.operator_id ?? schedule.operator_id,
    status: operation?.status ?? schedule.status,
    actualStartTime: operation && isActiveStatus(operation.status) ? operation.simulation_time ?? null : null,
    startTime: schedule.start_time,
    endTime: schedule.end_time,
    duration: schedule.end_time - schedule.start_time
  };
}

function dedupeSlots(slots: OperationSlot[]) {
  const seen = new Set<string>();
  return slots.filter((slot) => {
    if (seen.has(slot.operationId)) {
      return false;
    }
    seen.add(slot.operationId);
    return true;
  });
}

function readNumber(value: unknown) {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function currentStatePath(path: string, scenarioId: number | null, limit: number) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (scenarioId !== null) {
    params.set('scenario_id', String(scenarioId));
  }
  return `${path}?${params.toString()}`;
}

function calculateProgress(slot: OperationSlot, currentSimTime: number): OperationProgress {
  const effectiveStartTime = slot.actualStartTime ?? slot.startTime;
  if (effectiveStartTime === null) {
    const total = Math.max(0, slot.duration ?? 0);
    return { isScheduled: false, elapsed: 0, remaining: total, total, percent: 0 };
  }
  const total = Math.max(1, slot.duration ?? (slot.endTime !== null ? slot.endTime - effectiveStartTime : 0));
  const elapsed = clamp(Math.round(currentSimTime - effectiveStartTime), 0, total);
  const remaining = clamp(total - elapsed, 0, total);
  const percent = clamp(Math.round((elapsed / total) * 100), 0, 100);
  return { isScheduled: true, elapsed, remaining, total, percent };
}

function isActiveStatus(status: string) {
  return ['Running', 'Setup', 'QC', 'Rework'].includes(status);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function lineMatchesFilter(line: MachineLine, filter: MachineViewFilter) {
  if (filter === 'active') {
    return line.current !== null || line.backlogCount > 0;
  }
  if (filter === 'running') {
    return line.current !== null;
  }
  if (filter === 'queued') {
    return line.backlogCount > 0;
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
