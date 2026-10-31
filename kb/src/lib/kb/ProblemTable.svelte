<script lang="ts">
  import reports from '#lib/data/reports-4471.json';
  import notes from '#lib/data/desk-notes.json';
  import { problemOf, uniqueById, type Problem, type Report } from '#lib/kb/causes';
  import { tenantOf } from '#lib/kb/locales';

  // Problem → where it is tracked now. Pass e.g. { parser: 'https://github.com/…/issues/1' }.
  let { ticket, tracked = {} }: { ticket: number; tracked?: Partial<Record<Problem, string>> } = $props();

  const merged = $derived(uniqueById(reports as Report[]).filter((r) => r.mergedInto === ticket));
  const rows = $derived.by(() => {
    const by = new Map<Problem, Report[]>();
    for (const r of merged) {
      const p = problemOf(r, tenantOf(r), notes.oneDayMove);
      by.set(p, [...(by.get(p) ?? []), r]);
    }
    return [...by.entries()]
      .map(([problem, rs]) => {
        const days = rs.map((r) => r.receivedAt.slice(0, 10)).sort();
        return { problem, count: rs.length, tenants: new Set(rs.map((r) => r.tenant)).size, first: days[0], last: days[days.length - 1] };
      })
      .sort((a, b) => b.count - a.count);
  });
</script>

<p class="sum">
  <strong>{merged.length}</strong> reports merged into #{ticket} · <strong>{rows.length}</strong>
  {rows.length === 1 ? 'problem' : 'problems'}
</p>

<table>
  <thead>
    <tr><th>problem</th><th>reports</th><th>tenants</th><th>seen</th><th>tracked in</th></tr>
  </thead>
  <tbody>
    {#each rows as r (r.problem)}
      <tr>
        <td><code>{r.problem}</code></td>
        <td>{r.count}</td>
        <td>{r.tenants}</td>
        <td>{r.first} → {r.last}</td>
        <td>{#if tracked[r.problem]}<a href={tracked[r.problem]}>issue</a>{:else}—{/if}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .sum { font-size: 1.1rem; }
</style>
