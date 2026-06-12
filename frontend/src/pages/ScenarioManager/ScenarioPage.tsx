import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { apiGet, apiPost } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { Scenario } from '../../types/api';

export function ScenarioPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState('New Scenario');
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios') });
  const createScenario = useMutation({
    mutationFn: () => apiPost<Scenario>('/scenarios', { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scenarios'] })
  });
  const forkScenario = useMutation({
    mutationFn: (scenarioId: number) => apiPost<Scenario>(`/scenarios/${scenarioId}/fork`, { name: `${name} Fork` }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scenarios'] })
  });
  const snapshotScenario = useMutation({
    mutationFn: (scenarioId: number) => apiPost(`/scenarios/${scenarioId}/snapshots`, { reason: 'Manual UI snapshot' })
  });

  return (
    <Page title="Scenarios" eyebrow="Scenario manager">
      <section className="rounded border border-zinc-200 bg-white p-4">
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            className="min-w-0 flex-1 rounded border border-zinc-300 px-3 py-2 text-sm"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <button className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white" type="button" onClick={() => createScenario.mutate()}>
            Create
          </button>
        </div>
      </section>
      {scenarios.error ? <ErrorState error={scenarios.error} /> : null}
      <section className="overflow-hidden rounded border border-zinc-200 bg-white">
        {scenarios.data?.length ? (
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500">
              <tr><th className="p-3">Name</th><th className="p-3">Status</th><th className="p-3">Parent</th><th className="p-3">Actions</th></tr>
            </thead>
            <tbody>
              {scenarios.data.map((scenario) => (
                <tr key={scenario.id} className="border-t border-zinc-200">
                  <td className="p-3 font-medium">{scenario.name}</td>
                  <td className="p-3"><Status value={scenario.status} /></td>
                  <td className="p-3">{scenario.parent_scenario_id ?? '-'}</td>
                  <td className="space-x-2 p-3">
                    <button className="rounded border border-zinc-300 px-2 py-1 text-xs" type="button" onClick={() => forkScenario.mutate(scenario.id)}>Fork</button>
                    <button className="rounded border border-zinc-300 px-2 py-1 text-xs" type="button" onClick={() => snapshotScenario.mutate(scenario.id)}>Snapshot</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState label="No scenarios yet." />
        )}
      </section>
    </Page>
  );
}
