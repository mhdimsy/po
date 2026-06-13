import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { Gantt, Task, ViewMode } from 'gantt-task-react';
import 'gantt-task-react/dist/index.css';

import { apiGet, apiPost } from '../../api/client';
import { LoadingButton } from '../../components/LoadingButton';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { OptimizationRun, Scenario, ScheduleOperation } from '../../types/api';

const BASE_DATE = new Date(2026, 0, 1, 6, 0, 0);

type MoveDraft = {
  start_time: number;
  end_time: number;
};

type ValidationResult = {
  valid: boolean;
  reasons: string[];
};

export function SchedulePage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [runId, setRunId] = useState<number | null>(null);
  const [draftMoves, setDraftMoves] = useState<Record<number, MoveDraft>>({});
  const [conflicts, setConflicts] = useState<string[]>([]);
  const [lastValidMove, setLastValidMove] = useState<string | null>(null);
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios') });
  const runs = useQuery({ queryKey: ['optimizer-runs', scenarioId], queryFn: () => apiGet<OptimizationRun[]>(`/optimizer/runs?scenario_id=${scenarioId}`), enabled: scenarioId !== null });
  const schedule = useQuery({ queryKey: ['schedule', runId], queryFn: () => apiGet<ScheduleOperation[]>(`/optimizer/runs/${runId}/schedule`), enabled: runId !== null });
  const runOptimizer = useMutation({
    mutationFn: () => apiPost<{ run: OptimizationRun; schedule: ScheduleOperation[] }>('/optimizer/run', { scenario_id: scenarioId }),
    onSuccess: (data) => {
      setRunId(data.run.id);
      runs.refetch();
      schedule.refetch();
    }
  });
  const accept = useMutation({ mutationFn: () => apiPost(`/optimizer/runs/${runId}/accept`), onSuccess: () => runs.refetch() });

  const effectiveSchedule = useMemo(
    () => (schedule.data ?? []).map((item) => ({ ...item, ...(draftMoves[item.id] ?? {}) })),
    [schedule.data, draftMoves]
  );
  const ganttTasks = useMemo(() => toGanttTasks(effectiveSchedule), [effectiveSchedule]);

  const handleDateChange = (task: Task) => {
    const scheduleId = Number(task.id.replace('schedule-', ''));
    const item = effectiveSchedule.find((candidate) => candidate.id === scheduleId);
    if (!item) {
      setConflicts(['Operation was not found in the current schedule.']);
      return false;
    }

    const proposedMove = {
      start_time: minuteFromDate(task.start),
      end_time: Math.max(minuteFromDate(task.start) + 1, minuteFromDate(task.end))
    };
    const validation = validateManualMove(item, proposedMove, effectiveSchedule);
    if (!validation.valid) {
      setConflicts(validation.reasons);
      setLastValidMove(null);
      return false;
    }

    setConflicts([]);
    setLastValidMove(`${item.operation_id}: ${proposedMove.start_time} - ${proposedMove.end_time}`);
    setDraftMoves((current) => ({ ...current, [item.id]: proposedMove }));
    return true;
  };

  return (
    <Page title="Gantt Schedule" eyebrow="Manual planning">
      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto_auto]">
          <select className="rounded border border-zinc-300 px-3 py-2 text-sm" value={scenarioId ?? ''} onChange={(event) => setScenarioId(event.target.value ? Number(event.target.value) : null)}>
            <option value="">Select scenario</option>
            {scenarios.data?.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
          <select className="rounded border border-zinc-300 px-3 py-2 text-sm" value={runId ?? ''} onChange={(event) => setRunId(event.target.value ? Number(event.target.value) : null)}>
            <option value="">Select run</option>
            {runs.data?.map((run) => <option key={run.id} value={run.id}>Run {run.id} · {run.status} · score {run.score}</option>)}
          </select>
          <LoadingButton disabled={!scenarioId} loading={runOptimizer.isPending} onClick={() => runOptimizer.mutate()}>Run</LoadingButton>
          <LoadingButton variant="secondary" disabled={!runId} loading={accept.isPending} onClick={() => accept.mutate()}>Accept</LoadingButton>
        </div>
      </section>
      {schedule.error ? <ErrorState error={schedule.error} /> : null}
      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm font-semibold">Machine timeline</div>
          <div className="flex flex-wrap gap-2">
            <Status value={`${effectiveSchedule.length} operations`} />
            <Status value={lastValidMove ? `Draft: ${lastValidMove}` : 'No draft move'} />
          </div>
        </div>
        {conflicts.length ? (
          <div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            <div className="font-semibold">Move blocked</div>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              {conflicts.map((reason) => <li key={reason}>{reason}</li>)}
            </ul>
          </div>
        ) : null}
        {ganttTasks.length ? (
          <div className="overflow-auto">
            <Gantt
              tasks={ganttTasks}
              viewMode={ViewMode.Hour}
              listCellWidth="190px"
              rowHeight={42}
              columnWidth={64}
              barCornerRadius={3}
              onDateChange={handleDateChange}
            />
          </div>
        ) : (
          <EmptyState label="No schedule selected for Gantt." />
        )}
      </section>
      <section className="overflow-hidden rounded border border-zinc-200 bg-white shadow-sm">
        {schedule.data?.length ? (
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500"><tr><th className="p-3">Operation</th><th className="p-3">Machine</th><th className="p-3">Operator</th><th className="p-3">Window</th><th className="p-3">Status</th><th className="p-3">Score</th></tr></thead>
            <tbody>{effectiveSchedule.map((item) => <tr key={item.id} className="border-t border-zinc-200"><td className="p-3 font-medium">{item.operation_id}</td><td className="p-3">{item.machine_id ?? '-'}</td><td className="p-3">{item.operator_id ?? '-'}</td><td className="p-3">{item.start_time} - {item.end_time}</td><td className="p-3"><Status value={item.status} /></td><td className="p-3">{item.score}</td></tr>)}</tbody>
          </table>
        ) : <EmptyState label="No suggested schedule selected." />}
      </section>
    </Page>
  );
}

function toGanttTasks(schedule: ScheduleOperation[]): Task[] {
  const machineGroups = Array.from(new Set(schedule.map((item) => item.machine_id ?? 'Unassigned Machine')));
  const projectTasks: Task[] = machineGroups.map((machineId, index) => {
    const machineItems = schedule.filter((item) => (item.machine_id ?? 'Unassigned Machine') === machineId);
    return {
      id: `machine-${machineId}`,
      name: `Machine ${machineId}`,
      type: 'project',
      start: dateFromMinute(Math.min(...machineItems.map((item) => item.start_time))),
      end: dateFromMinute(Math.max(...machineItems.map((item) => item.end_time))),
      progress: 0,
      hideChildren: false,
      displayOrder: index + 1,
      styles: { backgroundColor: '#0f766e', progressColor: '#0f766e' }
    };
  });

  const operationTasks: Task[] = schedule.map((item, index) => ({
    id: `schedule-${item.id}`,
    name: `${item.operation_id} · ${item.order_id ?? 'No order'} · OP ${item.operator_id ?? '-'}`,
    type: 'task',
    project: `machine-${item.machine_id ?? 'Unassigned Machine'}`,
    start: dateFromMinute(item.start_time),
    end: dateFromMinute(Math.max(item.start_time + 1, item.end_time)),
    progress: item.status === 'Accepted' ? 100 : item.status === 'Suggested' ? 35 : 0,
    displayOrder: machineGroups.length + index + 1,
    styles: {
      backgroundColor: item.status === 'Blocked' ? '#dc2626' : '#2563eb',
      backgroundSelectedColor: item.status === 'Blocked' ? '#b91c1c' : '#1d4ed8',
      progressColor: item.status === 'Accepted' ? '#16a34a' : '#38bdf8',
      progressSelectedColor: '#15803d'
    }
  }));

  return [...projectTasks, ...operationTasks];
}

function validateManualMove(item: ScheduleOperation, move: MoveDraft, schedule: ScheduleOperation[]): ValidationResult {
  const reasons: string[] = [];
  if (move.start_time < 0) {
    reasons.push('Calendar blocked: start time cannot be before simulation minute 0.');
  }
  if (move.end_time <= move.start_time) {
    reasons.push('Calendar blocked: end time must be after start time.');
  }
  if (!isWorkingWindow(move.start_time, move.end_time)) {
    reasons.push('Calendar/shift blocked: operation must stay inside 06:00-22:00 working window.');
  }
  if (item.status === 'Blocked' || item.reason_json?.blocked_reason) {
    reasons.push(`QC/Approval/NCR or material blocker: ${item.reason_json?.blocked_reason ?? 'operation is blocked'}.`);
  }
  if (hasMachineConflict(item, move, schedule)) {
    reasons.push('Machine busy/down: selected machine has an overlapping operation.');
  }
  if (hasOperatorConflict(item, move, schedule)) {
    reasons.push('Operator unavailable/not authorized: selected operator has an overlapping operation.');
  }
  if (hasPrecedenceConflict(item, move, schedule)) {
    reasons.push('Operation precedence: previous operation for this order finishes after the proposed start.');
  }
  if (item.reason_json?.blocked_reason === 'material_unavailable') {
    reasons.push('Material unavailable: optimizer marked this operation as material-blocked.');
  }
  return { valid: reasons.length === 0, reasons };
}

function hasMachineConflict(item: ScheduleOperation, move: MoveDraft, schedule: ScheduleOperation[]) {
  if (!item.machine_id) return false;
  return schedule.some((candidate) => candidate.id !== item.id && candidate.machine_id === item.machine_id && overlaps(move, candidate));
}

function hasOperatorConflict(item: ScheduleOperation, move: MoveDraft, schedule: ScheduleOperation[]) {
  if (!item.operator_id) return false;
  return schedule.some((candidate) => candidate.id !== item.id && candidate.operator_id === item.operator_id && overlaps(move, candidate));
}

function hasPrecedenceConflict(item: ScheduleOperation, move: MoveDraft, schedule: ScheduleOperation[]) {
  if (!item.order_id) return false;
  const sameOrder = schedule
    .filter((candidate) => candidate.id !== item.id && candidate.order_id === item.order_id)
    .sort((left, right) => left.start_time - right.start_time);
  const previousOperations = sameOrder.filter((candidate) => candidate.start_time <= item.start_time);
  const previous = previousOperations.length ? previousOperations[previousOperations.length - 1] : undefined;
  return previous ? previous.end_time > move.start_time : false;
}

function overlaps(move: MoveDraft, candidate: ScheduleOperation) {
  return move.start_time < candidate.end_time && candidate.start_time < move.end_time;
}

function isWorkingWindow(startMinute: number, endMinute: number) {
  const startMinuteOfDay = startMinute % 1440;
  const endMinuteOfDay = endMinute % 1440;
  return startMinuteOfDay >= 360 && endMinuteOfDay <= 1320 && endMinuteOfDay > startMinuteOfDay;
}

function dateFromMinute(minute: number) {
  return new Date(BASE_DATE.getTime() + minute * 60_000);
}

function minuteFromDate(date: Date) {
  return Math.max(0, Math.round((date.getTime() - BASE_DATE.getTime()) / 60_000));
}
