import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';

import { apiUpload } from '../../api/client';
import { Page } from '../../components/Page';
import { EmptyState, ErrorState, Status } from '../../components/Status';
import type { ImportValidationReport } from '../../types/api';

export function ImportPage() {
  const [files, setFiles] = useState<File[]>([]);
  const validate = useMutation({
    mutationFn: () => apiUpload<ImportValidationReport>('/imports/validate', files)
  });
  const runImport = useMutation({
    mutationFn: () => apiUpload('/imports/run', files, { source_name: 'frontend-upload' })
  });

  return (
    <Page title="CSV Import" eyebrow="Factory data">
      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="rounded border border-zinc-200 bg-white p-4">
          <label className="block text-sm font-medium text-zinc-700" htmlFor="csv-files">
            CSV files
          </label>
          <input
            id="csv-files"
            multiple
            className="mt-3 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm"
            type="file"
            accept=".csv"
            onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          />
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:bg-zinc-300"
              type="button"
              disabled={!files.length || validate.isPending}
              onClick={() => validate.mutate()}
            >
              Validate
            </button>
            <button
              className="rounded border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-800 disabled:text-zinc-400"
              type="button"
              disabled={!files.length || runImport.isPending}
              onClick={() => runImport.mutate()}
            >
              Import
            </button>
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {files.map((file) => (
              <div key={file.name} className="rounded border border-zinc-200 px-3 py-2 text-sm">
                {file.name}
              </div>
            ))}
          </div>
        </div>
        <div className="rounded border border-zinc-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Validation report</h2>
            <Status value={validate.data ? (validate.data.import_ready ? 'Ready' : 'Blocked') : 'Idle'} />
          </div>
          {validate.error ? <div className="mt-3"><ErrorState error={validate.error} /></div> : null}
          {validate.data ? (
            <div className="mt-3 space-y-3 text-sm">
              <div>Total rows: {validate.data.total_rows}</div>
              <div>Issues: {validate.data.issues.length}</div>
              <div className="max-h-80 space-y-2 overflow-auto">
                {validate.data.issues.map((issue, index) => (
                  <div key={`${issue.file_name}-${issue.code}-${index}`} className="rounded border border-zinc-200 p-2">
                    <div className="font-medium">{issue.severity} · {issue.code}</div>
                    <div className="text-zinc-600">{issue.file_name}: {issue.message}</div>
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
