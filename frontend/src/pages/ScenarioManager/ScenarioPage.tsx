import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { apiGet, apiPost } from '../../api/client';
import { LoadingButton } from '../../components/LoadingButton';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { Scenario, ScenarioSeedResponse } from '../../types/api';

export function ScenarioPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState('New Scenario');
  const [maxOrders, setMaxOrders] = useState(500);
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
  const seedScenario = useMutation({
    mutationFn: (scenarioId: number) =>
      apiPost<ScenarioSeedResponse>(`/scenarios/${scenarioId}/seed-from-master-data`, {
        max_orders: maxOrders,
        reset_existing_state: true
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] });
      queryClient.invalidateQueries({ queryKey: ['manager-dashboard'] });
    }
  });

  return (
    <Page title="Scenarios" eyebrow="Scenario manager">
      <section className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row">
          <input
            className="min-w-0 flex-1 rounded border border-zinc-300 px-3 py-2 text-sm"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <label className="flex items-center gap-2 text-sm text-zinc-600">
            Orders
            <input
              className="w-28 rounded border border-zinc-300 px-3 py-2 text-sm"
              min={1}
              max={5000}
              type="number"
              value={maxOrders}
              onChange={(event) => setMaxOrders(Number(event.target.value))}
            />
          </label>
          <LoadingButton loading={createScenario.isPending} onClick={() => createScenario.mutate()}>
            Create
          </LoadingButton>
        </div>
      </section>
      {scenarios.error ? <ErrorState error={scenarios.error} /> : null}
      {seedScenario.error ? <ErrorState error={seedScenario.error} /> : null}
      {seedScenario.data ? (
        <div className="rounded border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
          Scenario initialized: {seedScenario.data.orders_seeded} orders, {seedScenario.data.operations_seeded} operations, {seedScenario.data.machines_seeded} machines.
        </div>
      ) : null}
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
                    <LoadingButton className="min-h-7 px-2 py-1 text-xs" variant="secondary" loading={forkScenario.isPending} onClick={() => forkScenario.mutate(scenario.id)}>Fork</LoadingButton>
                    <LoadingButton className="min-h-7 px-2 py-1 text-xs" variant="secondary" loading={snapshotScenario.isPending} onClick={() => snapshotScenario.mutate(scenario.id)}>Snapshot</LoadingButton>
                    <LoadingButton
                      className="min-h-7 px-2 py-1 text-xs"
                      variant="secondary"
                      disabled={seedScenario.isPending}
                      loading={seedScenario.isPending}
                      onClick={() => seedScenario.mutate(scenario.id)}
                    >
                      Initialize
                    </LoadingButton>
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
