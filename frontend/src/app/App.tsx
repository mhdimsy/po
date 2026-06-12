export function App() {
  return (
    <main className="min-h-screen bg-zinc-50 text-zinc-950">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-10">
        <p className="text-sm font-medium uppercase tracking-normal text-teal-700">
          Full Digital Twin Prototype
        </p>
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight">
          Factory production simulation workspace
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-zinc-700">
          Local V1 shell for CSV import, master data, simulation, scheduling, and operational dashboards.
        </p>
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {['Import', 'Master Data', 'Simulation'].map((item) => (
            <div key={item} className="rounded border border-zinc-200 bg-white p-4">
              <h2 className="text-sm font-semibold">{item}</h2>
              <p className="mt-2 text-sm text-zinc-600">Module placeholder</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
