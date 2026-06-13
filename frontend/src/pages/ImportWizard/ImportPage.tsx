import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';

import { apiPost, apiUpload } from '../../api/client';
import { LoadingButton } from '../../components/LoadingButton';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { ImportValidationReport, RebuildDemoResponse } from '../../types/api';

const requiredFiles = [
  'process_types.csv',
  'processes.csv',
  'work_centers.csv',
  'machines.csv',
  'machine_processes.csv',
  'bom.csv',
  'bom_parts.csv',
  'routings.csv',
  'routing_operations.csv',
  'orders.csv',
  'order_parts.csv'
];

const ISSUE_RENDER_LIMIT = 200;

export function ImportPage() {
  const [files, setFiles] = useState<File[]>([]);
  const filesByName = new Map(files.map((file) => [file.name, file]));
  const missingFiles = requiredFiles.filter((fileName) => !filesByName.has(fileName));
  const selectedRequiredFiles = requiredFiles.filter((fileName) => filesByName.has(fileName));
  const hasAllRequiredFiles = missingFiles.length === 0;
  const validate = useMutation({
    mutationFn: () => apiUpload<ImportValidationReport>('/imports/validate', files)
  });
  const runImport = useMutation({
    mutationFn: () => apiUpload('/imports/run', files, { source_name: 'frontend-upload' })
  });
  const rebuildDemo = useMutation({
    mutationFn: () => apiPost<RebuildDemoResponse>('/imports/rebuild-demo', { scenario_name: 'Factory Demo', max_orders: 500 })
  });
  const visibleIssues = validate.data?.issues.slice(0, ISSUE_RENDER_LIMIT) ?? [];
  const hiddenIssueCount = Math.max(0, (validate.data?.issues.length ?? 0) - ISSUE_RENDER_LIMIT);

  return (
    <Page title="CSV Import" eyebrow="Factory data">
      <section className="rounded border border-teal-200 bg-white p-5 shadow-sm">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_auto] xl:items-center">
          <div>
            <h2 className="text-lg font-semibold">One-click demo setup</h2>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-zinc-600">
              Rebuilds the dev database from repaired factory sample files, imports master data, and initializes a ready factory scenario.
            </p>
          </div>
          <LoadingButton
            className="px-5"
            loading={rebuildDemo.isPending}
            onClick={() => rebuildDemo.mutate()}
          >
            Rebuild Demo Database
          </LoadingButton>
        </div>
        {rebuildDemo.isPending ? (
          <div className="mt-4 overflow-hidden rounded border border-teal-100 bg-teal-50">
            <div className="conveyor-flow h-2" />
            <div className="px-3 py-2 text-sm text-teal-900">Repairing files, resetting schema, importing data, and creating the demo scenario...</div>
          </div>
        ) : null}
        {rebuildDemo.error ? <div className="mt-3"><ErrorState error={rebuildDemo.error} /></div> : null}
        {rebuildDemo.data ? (
          <div className="mt-3 grid gap-2 text-sm md:grid-cols-4">
            <Status value={`Batch ${rebuildDemo.data.import_report.import_batch_id}`} />
            <Status value={`${rebuildDemo.data.orders_seeded} orders`} />
            <Status value={`${rebuildDemo.data.operations_seeded} operations`} />
            <Status value={`${rebuildDemo.data.machines_seeded} machines`} />
          </div>
        ) : null}
      </section>
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_28rem]">
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <label className="block text-sm font-medium text-zinc-700" htmlFor="csv-files">
            CSV files
          </label>
          <input
            id="csv-files"
            multiple
            className="mt-3 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm"
            type="file"
            accept=".csv"
            onChange={(event) => {
              const incoming = Array.from(event.target.files ?? []);
              const next = new Map(files.map((file) => [file.name, file]));
              for (const file of incoming) {
                next.set(file.name, file);
              }
              setFiles(Array.from(next.values()).sort((a, b) => a.name.localeCompare(b.name)));
              event.currentTarget.value = '';
            }}
          />
          <div className="mt-3 text-sm text-zinc-600">
            {selectedRequiredFiles.length} of {requiredFiles.length} required files selected
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <LoadingButton
              disabled={!files.length || validate.isPending}
              loading={validate.isPending}
              onClick={() => validate.mutate()}
            >
              Validate
            </LoadingButton>
            <LoadingButton
              variant="secondary"
              disabled={!hasAllRequiredFiles || runImport.isPending}
              loading={runImport.isPending}
              onClick={() => runImport.mutate()}
            >
              Import
            </LoadingButton>
            <LoadingButton
              variant="secondary"
              disabled={!files.length || validate.isPending || runImport.isPending}
              onClick={() => {
                setFiles([]);
                validate.reset();
                runImport.reset();
              }}
            >
              Clear
            </LoadingButton>
          </div>
          {missingFiles.length ? (
            <div className="mt-4 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              Missing required files: {missingFiles.join(', ')}
            </div>
          ) : null}
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {requiredFiles.map((fileName) => {
              const file = filesByName.get(fileName);
              return (
                <div key={fileName} className="flex items-center justify-between gap-3 rounded border border-zinc-200 px-3 py-2 text-sm">
                  <span className={file ? 'font-medium text-zinc-800' : 'text-zinc-400'}>{fileName}</span>
                  <span className="shrink-0 text-xs text-zinc-500">{file ? formatBytes(file.size) : 'Missing'}</span>
                </div>
              );
            })}
          </div>
          {files.some((file) => !requiredFiles.includes(file.name)) ? (
            <div className="mt-4 rounded border border-zinc-200 p-3">
              <h2 className="text-sm font-semibold">Extra files ignored by validator</h2>
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {files.filter((file) => !requiredFiles.includes(file.name)).map((file) => (
                  <div key={file.name} className="rounded border border-zinc-200 px-3 py-2 text-sm text-zinc-500">
                    {file.name}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
        <div className="rounded border border-zinc-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Validation report</h2>
            <Status value={validate.data ? (validate.data.import_ready ? 'Ready' : 'Blocked') : 'Idle'} />
          </div>
          {validate.error ? <div className="mt-3"><ErrorState error={validate.error} /></div> : null}
          {runImport.error ? <div className="mt-3"><ErrorState error={runImport.error} /></div> : null}
          {runImport.data ? (
            <div className="mt-3 rounded border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
              Import request completed.
            </div>
          ) : null}
          {validate.data ? (
            <div className="mt-3 space-y-3 text-sm">
              <div>Total rows: {validate.data.total_rows}</div>
              <div>Issues: {validate.data.issues.length}</div>
              <div className="grid gap-2">
                {validate.data.files.map((file) => (
                  <div key={file.file_name} className="flex items-center justify-between rounded border border-zinc-200 px-2 py-1">
                    <span>{file.file_name}</span>
                    <span className="text-zinc-500">
                      {file.row_count} rows · {file.errors.length} errors · {file.warnings.length} warnings
                    </span>
                  </div>
                ))}
              </div>
              {hiddenIssueCount ? (
                <div className="rounded border border-amber-200 bg-amber-50 p-2 text-amber-900">
                  Showing first {ISSUE_RENDER_LIMIT} issues. {hiddenIssueCount} more are hidden to keep the UI responsive.
                </div>
              ) : null}
              <div className="max-h-80 space-y-2 overflow-auto">
                {visibleIssues.map((issue, index) => (
                  <div key={`${issue.file_name}-${issue.code}-${index}`} className="rounded border border-zinc-200 p-2">
                    <div className="font-medium">{issue.severity} · {issue.code}</div>
                    <div className="text-zinc-600">
                      {issue.file_name}
                      {issue.row_number ? `:${issue.row_number}` : ''}: {issue.message}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="mt-3"><EmptyState label="No validation run yet." /></div>
          )}
        </div>
      </section>
    </Page>
  );
}

function formatBytes(size: number) {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}
