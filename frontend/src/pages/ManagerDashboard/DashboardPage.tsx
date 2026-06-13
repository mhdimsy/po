import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiGet, apiPost, apiPut } from '../../api/client';
import { LoadingButton } from '../../components/LoadingButton';
import { Page } from '../../components/Page';
import { ErrorState, Status } from '../../components/Status';
import type {
  ManagerDashboard,
  RiskCalculationResponse,
  RiskSettings,
  Scenario
} from '../../types/api';

const settingLabels: Array<{ key: keyof RiskSettings; label: string }> = [
  { key: 'delay_risk_weight', label: 'Delay' },
  { key: 'material_shortage_risk_weight', label: 'Material shortage' },
  { key: 'machine_failure_risk_weight', label: 'Machine failure' },
  { key: 'qc_ncr_risk_weight', label: 'QC/NCR' },
  { key: 'schedule_instability_weight', label: 'Instability' },
  { key: 'low_threshold', label: 'Low threshold' },
  { key: 'medium_threshold', label: 'Medium threshold' },
  { key: 'high_threshold', label: 'High threshold' }
];

export function DashboardPage() {
  const queryClient = useQueryClient();
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: () => apiGet<Scenario[]>('/scenarios') });
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null);
  const dashboardPath = selectedScenarioId ? `/dashboard/manager?scenario_id=${selectedScenarioId}` : '/dashboard/manager';
  const dashboard = useQuery({
    queryKey: ['manager-dashboard', selectedScenarioId],
    queryFn: () => apiGet<ManagerDashboard>(dashboardPath)
  });
  const riskSettings = useQuery({ queryKey: ['risk-settings'], queryFn: () => apiGet<RiskSettings>('/risk/settings') });
  const [settingsDraft, setSettingsDraft] = useState<RiskSettings | null>(null);

  useEffect(() => {
    if (riskSettings.data) {
      setSettingsDraft(riskSettings.data);
    }
  }, [riskSettings.data]);

  useEffect(() => {
    if (selectedScenarioId === null && scenarios.data?.[0]?.id) {
      setSelectedScenarioId(scenarios.data[0].id);
    }
  }, [scenarios.data, selectedScenarioId]);

  const saveSettings = useMutation({
    mutationFn: (settings: RiskSettings) => apiPut<RiskSettings>('/risk/settings', settings),
    onSuccess: (settings) => {
      setSettingsDraft(settings);
      queryClient.invalidateQueries({ queryKey: ['risk-settings'] });
    }
  });

  const calculateRisk = useMutation({
    mutationFn: (scenarioId: number) => apiPost<RiskCalculationResponse>(`/risk/calculate/${scenarioId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-dashboard'] });
    }
  });

  const summaryCards = dashboard.data
    ? [
        { label: 'On-time rate', value: `${dashboard.data.delivery.on_time_rate_percent}%` },
        { label: 'Delayed orders', value: dashboard.data.delivery.delayed_orders },
        { label: 'Production done', value: `${dashboard.data.production_progress.completion_percent}%` },
        { label: 'Machine use', value: `${dashboard.data.capacity.machine_utilization_percent}%` },
        { label: 'Material shortages', value: dashboard.data.material_shortage.shortage_items },
        { label: 'Open NCRs', value: dashboard.data.ncr_rework.open_ncrs }
      ]
    : [];

  return (
    <Page
      title="Dashboard"
      eyebrow="Manager overview"
      actions={
        <>
          <select
            className="h-9 rounded border border-zinc-300 bg-white px-3 text-sm"
            value={selectedScenarioId ?? ''}
            onChange={(event) => setSelectedScenarioId(event.target.value ? Number(event.target.value) : null)}
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
            disabled={!selectedScenarioId || calculateRisk.isPending}
            loading={calculateRisk.isPending}
            onClick={() => selectedScenarioId && calculateRisk.mutate(selectedScenarioId)}
          >
            Calculate risk
          </LoadingButton>
        </>
      }
    >
      {dashboard.error ? <ErrorState error={dashboard.error} /> : null}
      {riskSettings.error ? <ErrorState error={riskSettings.error} /> : null}
      {calculateRisk.error ? <ErrorState error={calculateRisk.error} /> : null}
      {saveSettings.error ? <ErrorState error={saveSettings.error} /> : null}

      <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        {summaryCards.map((card) => (
          <div key={card.label} className="rounded border border-zinc-200 bg-white p-4">
            <div className="text-sm text-zinc-500">{card.label}</div>
            <div className="mt-3 text-2xl font-semibold">{card.value}</div>
          </div>
        ))}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[minmax(0,1.55fr)_minmax(24rem,0.75fr)]">
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold">Operational dashboard</h2>
            <Status value={dashboard.isFetching ? 'Refreshing' : 'Idle'} />
          </div>
          {dashboard.data ? (
            <div className="grid gap-3 md:grid-cols-2">
              <MetricGroup
                title="Delay"
                rows={[
                  ['Delayed operations', dashboard.data.delay.delayed_operations],
                  ['Waiting material', dashboard.data.delay.waiting_material_operations],
                  ['Waiting machine', dashboard.data.delay.waiting_machine_operations],
                  ['Waiting QC', dashboard.data.delay.waiting_qc_operations]
                ]}
              />
              <MetricGroup
                title="Capacity"
                rows={[
                  ['Machines', dashboard.data.capacity.total_machines],
                  ['Busy machines', dashboard.data.capacity.busy_machines],
                  ['Unavailable machines', dashboard.data.capacity.unavailable_machines],
                  ['Operators busy', dashboard.data.capacity.busy_operators]
                ]}
              />
              <MetricGroup
                title="NCR and rework"
                rows={[
                  ['Open NCRs', dashboard.data.ncr_rework.open_ncrs],
                  ['High severity', dashboard.data.ncr_rework.high_severity_ncrs],
                  ['Active rework', dashboard.data.ncr_rework.active_rework_orders],
                  ['Delay min', dashboard.data.ncr_rework.estimated_delay_min]
                ]}
              />
              <MetricGroup
                title="Optimizer"
                rows={[
                  ['Latest run', dashboard.data.optimizer_performance.latest_run_id ?? '-'],
                  ['Status', dashboard.data.optimizer_performance.status ?? '-'],
                  ['Score', dashboard.data.optimizer_performance.score ?? '-'],
                  ['Changed ops', dashboard.data.optimizer_performance.changed_operations_count]
                ]}
              />
            </div>
          ) : null}
        </div>

        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold">Risk settings</h2>
          {settingsDraft ? (
            <div className="mt-3 grid gap-3">
              {settingLabels.map((setting) => (
                <label key={setting.key} className="grid gap-1 text-sm">
                  <span className="text-zinc-600">{setting.label}</span>
                  <input
                    className="h-9 rounded border border-zinc-300 px-2"
                    min={0}
                    step="0.1"
                    type="number"
                    value={settingsDraft[setting.key]}
                    onChange={(event) =>
                      setSettingsDraft({ ...settingsDraft, [setting.key]: Number(event.target.value) })
                    }
                  />
                </label>
              ))}
              <LoadingButton
                className="h-9"
                variant="dark"
                disabled={saveSettings.isPending}
                loading={saveSettings.isPending}
                onClick={() => settingsDraft && saveSettings.mutate(settingsDraft)}
              >
                Save settings
              </LoadingButton>
            </div>
          ) : null}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold">Bottlenecks</h2>
          <div className="mt-3 space-y-2 text-sm">
            {dashboard.data?.bottleneck.length ? (
              dashboard.data.bottleneck.map((item) => (
                <div key={item.resource_id} className="flex items-center justify-between rounded border border-zinc-200 p-2">
                  <span>{item.resource_id}</span>
                  <span className="font-medium">{item.queued_operations} queued</span>
                </div>
              ))
            ) : (
              <div className="text-zinc-500">No bottleneck data</div>
            )}
          </div>
        </div>

        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold">Top risk scores</h2>
          <div className="mt-3 space-y-2 text-sm">
            {dashboard.data?.risk.length ? (
              dashboard.data.risk.slice(0, 6).map((score) => (
                <div key={score.id} className="grid grid-cols-[1fr_auto] gap-3 rounded border border-zinc-200 p-2">
                  <div>
                    <div className="font-medium">
                      {score.aggregate_type} {score.aggregate_id}
                    </div>
                    <div className="text-zinc-500">{score.level}</div>
                  </div>
                  <div className="text-lg font-semibold">{score.total_score}</div>
                </div>
              ))
            ) : (
              <div className="text-zinc-500">No risk scores calculated</div>
            )}
          </div>
        </div>
      </section>
    </Page>
  );
}

function MetricGroup({ title, rows }: { title: string; rows: Array<[string, string | number]> }) {
  return (
    <div className="rounded border border-zinc-200 p-3">
      <h3 className="text-sm font-medium">{title}</h3>
      <div className="mt-3 space-y-2 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-3">
            <span className="text-zinc-500">{label}</span>
            <span className="font-medium">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
