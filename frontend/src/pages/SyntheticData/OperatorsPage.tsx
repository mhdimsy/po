import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiGet, apiPost } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { Operator } from '../../types/api';

export function OperatorsPage() {
  const queryClient = useQueryClient();
  const operators = useQuery({ queryKey: ['operators'], queryFn: () => apiGet<Operator[]>('/synthetic/operators?limit=100') });
  const generate = useMutation({
    mutationFn: () => apiPost('/synthetic/operators/generate', { count: 500, multi_skill_ratio: 0.25 }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['operators'] })
  });

  return (
    <Page
      title="Operators"
      eyebrow="Synthetic human resources"
      actions={<button className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white" type="button" onClick={() => generate.mutate()}>Generate 500</button>}
    >
      {operators.error ? <ErrorState error={operators.error} /> : null}
      <section className="overflow-hidden rounded border border-zinc-200 bg-white">
        {operators.data?.length ? (
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-50 text-xs uppercase tracking-normal text-zinc-500">
              <tr><th className="p-3">Code</th><th className="p-3">Name</th><th className="p-3">WorkCenter</th><th className="p-3">Status</th></tr>
            </thead>
            <tbody>
              {operators.data.map((operator) => (
                <tr key={operator.id} className="border-t border-zinc-200">
                  <td className="p-3 font-medium">{operator.code}</td>
                  <td className="p-3">{operator.full_name}</td>
                  <td className="p-3">{operator.home_work_center_id ?? '-'}</td>
                  <td className="p-3"><Status value={operator.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState label="No operators loaded." />
        )}
      </section>
    </Page>
  );
}
