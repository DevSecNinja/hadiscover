export interface Repository {
  name: string;
  owner: string;
  description: string | null;
  url: string;
  stars: number;
}

export interface Automation {
  id: number;
  alias: string | null;
  description: string | null;
  trigger_types: string[];
  blueprint_path: string | null;
  action_calls: string[];
  source_file_path: string;
  github_url: string;
  start_line: number | null;
  end_line: number | null;
  repository: Repository;
  indexed_at: string | null;
}

export interface RepositoryFacet {
  owner: string;
  name: string;
  stars: number;
  count: number;
}

export interface BlueprintFacet {
  path: string;
  count: number;
}

export interface TriggerFacet {
  type: string;
  count: number;
}

export interface ActionDomainFacet {
  domain: string;
  count: number;
}

export interface ActionFacet {
  call: string;
  count: number;
}

export interface Facets {
  repositories: RepositoryFacet[];
  blueprints: BlueprintFacet[];
  triggers: TriggerFacet[];
  action_domains: ActionDomainFacet[];
  actions: ActionFacet[];
}

export interface Statistics {
  total_repositories: number;
  total_automations: number;
  last_indexed_at: string | null;
  repo_star_count: number;
}

export interface SearchIndex {
  version: number;
  generated_at: string;
  statistics: Statistics;
  automations: Automation[];
}

export interface SearchFilters {
  repo: string | null;
  blueprint: string | null;
  trigger: string | null;
  actionDomain: string | null;
  action: string | null;
}

export interface SearchResult {
  results: Automation[];
  total: number;
  facets: Facets;
}

export const EMPTY_FACETS: Facets = {
  repositories: [],
  blueprints: [],
  triggers: [],
  action_domains: [],
  actions: [],
};

export function searchAutomations(
  index: SearchIndex,
  query: string,
  filters: SearchFilters,
  page: number,
  perPage: number,
): SearchResult {
  const constrainedPage = Math.max(1, page);
  const constrainedPerPage = Math.min(100, Math.max(10, perPage));
  const filtered = filterAutomations(index.automations, query, filters);
  const offset = (constrainedPage - 1) * constrainedPerPage;

  return {
    results: filtered.slice(offset, offset + constrainedPerPage),
    total: filtered.length,
    facets: buildFacets(index.automations, query, filters),
  };
}

function filterAutomations(
  automations: Automation[],
  query: string,
  filters: SearchFilters,
): Automation[] {
  const normalizedQuery = normalize(query);

  return automations.filter((automation) => {
    if (normalizedQuery && !matchesQuery(automation, normalizedQuery)) {
      return false;
    }
    return matchesFilters(automation, filters);
  });
}

function matchesQuery(
  automation: Automation,
  normalizedQuery: string,
): boolean {
  const repository = automation.repository;
  const values = [
    automation.alias,
    automation.description,
    automation.trigger_types.join(","),
    automation.action_calls.join(","),
    repository.owner,
    repository.name,
    repository.description,
  ];

  return values.some((value) => normalize(value).includes(normalizedQuery));
}

function matchesFilters(
  automation: Automation,
  filters: SearchFilters,
): boolean {
  if (filters.repo) {
    const repoName = `${automation.repository.owner}/${automation.repository.name}`;
    if (repoName !== filters.repo) return false;
  }

  if (filters.blueprint && automation.blueprint_path !== filters.blueprint) {
    return false;
  }

  if (filters.trigger && !automation.trigger_types.includes(filters.trigger)) {
    return false;
  }

  if (
    filters.actionDomain &&
    !automation.action_calls.some(
      (actionCall) => extractActionDomain(actionCall) === filters.actionDomain,
    )
  ) {
    return false;
  }

  if (filters.action && !automation.action_calls.includes(filters.action)) {
    return false;
  }

  return true;
}

function buildFacets(
  automations: Automation[],
  query: string,
  filters: SearchFilters,
): Facets {
  const repoScope = filterAutomations(automations, query, {
    ...filters,
    repo: null,
  });
  const blueprintScope = filterAutomations(automations, query, {
    ...filters,
    blueprint: null,
  });
  const triggerScope = filterAutomations(automations, query, {
    ...filters,
    trigger: null,
  });
  const actionDomainScope = filterAutomations(automations, query, {
    ...filters,
    actionDomain: null,
  });
  const actionScope = filterAutomations(automations, query, {
    ...filters,
    action: null,
  });

  return {
    repositories: buildRepositoryFacets(repoScope),
    blueprints: buildValueFacets(blueprintScope, (automation) => [
      automation.blueprint_path,
    ]).map(({ value, count }) => ({ path: value, count })),
    triggers: buildValueFacets(
      triggerScope,
      (automation) => automation.trigger_types,
    ).map(({ value, count }) => ({ type: value, count })),
    action_domains: buildValueFacets(actionDomainScope, (automation) =>
      automation.action_calls.map(extractActionDomain).filter(Boolean),
    ).map(({ value, count }) => ({ domain: value, count })),
    actions: buildValueFacets(
      actionScope,
      (automation) => automation.action_calls,
    ).map(({ value, count }) => ({ call: value, count })),
  };
}

function buildRepositoryFacets(automations: Automation[]): RepositoryFacet[] {
  const counts = new Map<string, RepositoryFacet>();

  for (const automation of automations) {
    const repository = automation.repository;
    const key = `${repository.owner}/${repository.name}`;
    const existing = counts.get(key);
    if (existing) {
      existing.count += 1;
    } else {
      counts.set(key, {
        owner: repository.owner,
        name: repository.name,
        stars: repository.stars || 0,
        count: 1,
      });
    }
  }

  return sortAndLimit([...counts.values()]);
}

function buildValueFacets(
  automations: Automation[],
  getValues: (automation: Automation) => (string | null)[],
): { value: string; count: number }[] {
  const counts = new Map<string, number>();

  for (const automation of automations) {
    for (const value of getValues(automation)) {
      if (!value) continue;
      counts.set(value, (counts.get(value) ?? 0) + 1);
    }
  }

  return sortAndLimit(
    [...counts.entries()].map(([value, count]) => ({ value, count })),
  );
}

function sortAndLimit<T extends { count: number }>(items: T[]): T[] {
  return items.sort((left, right) => right.count - left.count).slice(0, 20);
}

function extractActionDomain(actionCall: string): string {
  return actionCall.includes(".") ? actionCall.split(".")[0] : "";
}

function normalize(value: string | null | undefined): string {
  return (value ?? "").toLowerCase();
}
