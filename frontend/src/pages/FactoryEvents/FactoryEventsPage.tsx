import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { apiGet } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { FactoryEvent, Scenario } from '../../types/api';

const EVENT_TYPE_OPTIONS = [
  '',
  'SimulationStepped',
  'OperationScheduled',
  'OperationSetup',
  'OperationStarted',
  'OperationFinished',
  'ScheduleSuggested',
  'ScheduleAccepted',
  'ScenarioSeededFromMasterData'
];

const AGGREGATE_TYPE_OPTIONS = ['', 'Operation', 'Machine', 'Operator', 'Order', 'Scenario', 'OptimizationRun', 'SimulationRun'];

export function FactoryEventsPage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [eventType, setEventType] = useState('');
  const [aggregateType, setAggregateType] = useState('');
  const [aggregateId, setAggregateId] = useState('');
  const [orderId, setOrderId] = useState('');
  const [limit, setLimit] = useState(200);
  const [refreshSeconds, setRefreshSeconds] = useState(3);
  const refetchInterval = Math.max(1, refreshSeconds) * 1000;

  const scenarios = useQuery({ queryKey: ['event-scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios'), refetchInterval });
  const activeScenarioId = scenarioId ?? scenarios.data?.[0]?.id ?? null;
  const events = useQuery({
    queryKey: ['factory-events-table', activeScenarioId, eventType, aggregateType, aggregateId, orderId, limit],
    queryFn: () => apiGet<FactoryEvent[]>(eventsPath(activeScenarioId, eventType, aggregateType, aggregateId, orderId, limit)),
    enabled: activeScenarioId !== null,
    refetchInterval
  });
  const summary = useMemo(() => summarizeEvents(events.data ?? []), [events.data]);

  return (
    <Page
      title="Factory Events"
      eyebrow="Event store"
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
          <select className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm" value={eventType} onChange={(event) => setEventType(event.target.value)}>
            {EVENT_TYPE_OPTIONS.map((value) => (
              <option key={value || 'all'} value={value}>
                {value || 'All event types'}
              </option>
            ))}
          </select>
          <select className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm" value={aggregateType} onChange={(event) => setAggregateType(event.target.value)}>
            {AGGREGATE_TYPE_OPTIONS.map((value) => (
              <option key={value || 'all'} value={value}>
                {value || 'All aggregates'}
              </option>
            ))}
          </select>
          <input
            className="h-9 w-36 rounded border border-zinc-300 bg-white px-3 text-sm"
            placeholder="Aggregate id"
            value={aggregateId}
            onChange={(event) => setAggregateId(event.target.value)}
          />
          <input
            className="h-9 w-28 rounded border border-zinc-300 bg-white px-3 text-sm"
            placeholder="Order id"
            value={orderId}
            onChange={(event) => setOrderId(event.target.value)}
          />
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Limit</span>
            <input className="w-14 bg-transparent text-right outline-none" min={10} max={1000} type="number" value={limit} onChange={(event) => setLimit(Number(event.target.value))} />
          </label>
          <label className="flex items-center gap-2 rounded border border-zinc-300 bg-white px-3 text-sm">
            <span className="text-zinc-500">Refresh</span>
            <input className="w-12 bg-transparent text-right outline-none" min={1} max={60} type="number" value={refreshSeconds} onChange={(event) => setRefreshSeconds(Number(event.target.value))} />
            <span className="text-zinc-500">s</span>
          </label>
        </>
      }
    >
      {events.error ? <ErrorState error={events.error} /> : null}

      <section className="grid gap-4 md:grid-cols-4">
        <EventMetric label="Loaded events" value={events.data?.length ?? 0} subLabel={`limit ${limit}`} />
        <EventMetric label="Event types" value={summary.eventTypes} subLabel="in current result" />
        <EventMetric label="Latest sim time" value={summary.latestSimulationTime ?? '-'} subLabel="simulation minute" />
        <EventMetric label="Refresh" value={`${refreshSeconds}s`} subLabel={events.isFetching ? 'refreshing now' : 'live polling'} />
      </section>

      <section className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
        <div className="mb-4 flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-base font-semibold">Factory event table</h2>
            <div className="mt-1 text-sm text-zinc-500">Newest events are shown first. Use aggregate id for one order, machine, operation, run, or scenario.</div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Status value={activeScenarioId ? `Scenario ${activeScenarioId}` : 'No scenario'} />
            <Status value={events.isFetching ? 'Refreshing' : 'Live'} />
          </div>
        </div>

        {events.data?.length ? (
          <div className="overflow-auto">
            <table className="w-full min-w-[1100px] text-left text-sm">
              <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500">
                <tr>
                  <th className="p-3">ID</th>
                  <th className="p-3">Time</th>
                  <th className="p-3">Event</th>
                  <th className="p-3">Aggregate</th>
                  <th className="p-3">Simulation</th>
                  <th className="p-3">Payload</th>
                  <th className="p-3">Created</th>
                </tr>
              </thead>
              <tbody>
                {events.data.map((event) => (
                  <tr key={event.event_id} className="border-t border-zinc-200 align-top">
                    <td className="p-3 font-medium">{event.event_id}</td>
                    <td className="p-3">{event.created_at ? new Date(event.created_at).toLocaleTimeString() : '-'}</td>
                    <td className="p-3"><Status value={event.event_type} /></td>
                    <td className="p-3">
                      <div className="font-medium">{event.aggregate_type}</div>
                      <div className="mt-1 text-xs text-zinc-500">{event.aggregate_id}</div>
                    </td>
                    <td className="p-3">t={event.simulation_time ?? '-'}</td>
                    <td className="max-w-[28rem] p-3">
                      <div className="line-clamp-3 rounded bg-zinc-50 px-2 py-1 font-mono text-xs text-zinc-700">
                        {formatPayload(event.payload_json)}
                      </div>
                    </td>
                    <td className="p-3 text-xs text-zinc-500">{event.created_at ? new Date(event.created_at).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState label="No events match these filters." />
        )}
      </section>
    </Page>
  );
}

function EventMetric({ label, value, subLabel }: { label: string; value: string | number; subLabel: string }) {
  return (
    <div className="rounded border border-zinc-200 bg-white p-4 shadow-sm">
      <div className="text-sm text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-zinc-500">{subLabel}</div>
    </div>
  );
}

function eventsPath(scenarioId: number | null, eventType: string, aggregateType: string, aggregateId: string, orderId: string, limit: number) {
  const params = new URLSearchParams({ limit: String(Math.min(1000, Math.max(10, limit))) });
  if (scenarioId !== null) {
    params.set('scenario_id', String(scenarioId));
  }
  if (eventType) {
    params.set('event_type', eventType);
  }
  if (aggregateType) {
    params.set('aggregate_type', aggregateType);
  }
  if (aggregateId.trim()) {
    params.set('aggregate_id', aggregateId.trim());
  }
  if (orderId.trim()) {
    params.set('order_id', orderId.trim());
  }
  return `/events?${params.toString()}`;
}

function summarizeEvents(events: FactoryEvent[]) {
  const eventTypes = new Set(events.map((event) => event.event_type)).size;
  const latestSimulationTime = events.find((event) => event.simulation_time !== null)?.simulation_time ?? null;
  return { eventTypes, latestSimulationTime };
}

function formatPayload(payload: Record<string, unknown>) {
  const entries = Object.entries(payload ?? {});
  if (!entries.length) {
    return '{}';
  }
  return entries.map(([key, value]) => `${key}: ${String(value)}`).join(' · ');
}
