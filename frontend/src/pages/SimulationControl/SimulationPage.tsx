import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { apiGet, apiPost } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { Scenario, SimulationRun } from '../../types/api';

export function SimulationPage() {
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios') });
  const runs = useQuery({
    queryKey: ['simulation-runs', scenarioId],
    queryFn: () => apiGet<SimulationRun[]>(`/simulations/${scenarioId}/runs`),
    enabled: scenarioId !== null
  });
  const start = useMutation({ mutationFn: () => apiPost(`/simulations/${scenarioId}/start`, { speed_factor: 1, start_time: 0 }), onSuccess: () => runs.refetch() });
  const pause = useMutation({ mutationFn: () => apiPost(`/simulations/${scenarioId}/pause`), onSuccess: () => runs.refetch() });
  const resume = useMutation({ mutationFn: () => apiPost(`/simulations/${scenarioId}/resume`), onSuccess: () => runs.refetch() });
  const step = useMutation({ mutationFn: () => apiPost(`/simulations/${scenarioId}/step`, { minutes: 1 }), onSuccess: () => runs.refetch() });

  return (
    <Page title="Simulation Control" eyebrow="Runtime">
      <section className="rounded border border-zinc-200 bg-white p-4">
        <label className="block text-sm font-medium" htmlFor="scenario">Scenario</label>
        <select
          id="scenario"
          className="mt-2 w-full max-w-md rounded border border-zinc-300 px-3 py-2 text-sm"
          value={scenarioId ?? ''}
          onChange={(event) => setScenarioId(event.target.value ? Number(event.target.value) : null)}
        >
          <option value="">Select scenario</option>
          {scenarios.data?.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
        </select>
        <div className="mt-4 flex flex-wrap gap-2">
          <button className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:bg-zinc-300" disabled={!scenarioId} type="button" onClick={() => start.mutate()}>Start</button>
          <button className="rounded border border-zinc-300 px-3 py-2 text-sm disabled:text-zinc-400" disabled={!scenarioId} type="button" onClick={() => pause.mutate()}>Pause</button>
          <button className="rounded border border-zinc-300 px-3 py-2 text-sm disabled:text-zinc-400" disabled={!scenarioId} type="button" onClick={() => resume.mutate()}>Resume</button>
          <button className="rounded border border-zinc-300 px-3 py-2 text-sm disabled:text-zinc-400" disabled={!scenarioId} type="button" onClick={() => step.mutate()}>Step +1m</button>
        </div>
      </section>
      {runs.error ? <ErrorState error={runs.error} /> : null}
      <section className="overflow-hidden rounded border border-zinc-200 bg-white">
        {runs.data?.length ? (
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500"><tr><th className="p-3">Run</th><th className="p-3">Status</th><th className="p-3">Time</th><th className="p-3">Speed</th></tr></thead>
            <tbody>{runs.data.map((run) => <tr key={run.id} className="border-t border-zinc-200"><td className="p-3">{run.id}</td><td className="p-3"><Status value={run.status} /></td><td className="p-3">{run.current_sim_time}m</td><td className="p-3">{run.speed_factor}</td></tr>)}</tbody>
          </table>
        ) : <EmptyState label="No simulation runs for selected scenario." />}
      </section>
    </Page>
  );
}
