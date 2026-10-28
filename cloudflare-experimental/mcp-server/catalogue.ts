export interface CatalogueEntry {
  id: string;
  title: string;
  creator?: string;
  share_url: string;
  created_at?: string;
  description?: string;
  status?: string;
  visibility: "public" | "link_only";
  source: "user_manifest";
}

export interface CatalogueManifest {
  version: 1;
  owner_user_id?: string;
  entries: CatalogueEntry[];
}

const entryKeys = new Set([
  "id", "title", "creator", "share_url", "created_at", "description",
  "status", "visibility", "source",
]);

function requiredString(value: unknown, field: string, maxLength: number): string {
  if (typeof value !== "string" || !value.trim() || value.length > maxLength) {
    throw new Error(`Invalid catalogue ${field}`);
  }
  return value.trim();
}

function optionalString(value: unknown, field: string, maxLength: number): string | undefined {
  if (value === undefined) return undefined;
  return requiredString(value, field, maxLength);
}

function validateShareUrl(value: unknown): string {
  const text = requiredString(value, "share_url", 2048);
  let url: URL;
  try { url = new URL(text); } catch { throw new Error("Invalid catalogue share_url"); }
  if (url.protocol !== "https:" || !["suno.com", "www.suno.com"].includes(url.hostname)) {
    throw new Error("Catalogue share_url must be an HTTPS Suno share link");
  }
  return url.toString();
}

function validateEntry(value: unknown): CatalogueEntry {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Invalid catalogue entry");
  }
  const raw = value as Record<string, unknown>;
  for (const key of Object.keys(raw)) {
    if (!entryKeys.has(key)) throw new Error(`Unsupported catalogue field: ${key}`);
  }
  const visibility = raw.visibility;
  if (visibility !== "public" && visibility !== "link_only") {
    throw new Error("Invalid catalogue visibility");
  }
  if (raw.source !== "user_manifest") throw new Error("Invalid catalogue source");
  const createdAt = optionalString(raw.created_at, "created_at", 64);
  if (createdAt !== undefined && Number.isNaN(Date.parse(createdAt))) {
    throw new Error("Invalid catalogue created_at");
  }
  return {
    id: requiredString(raw.id, "id", 128),
    title: requiredString(raw.title, "title", 200),
    creator: optionalString(raw.creator, "creator", 200),
    share_url: validateShareUrl(raw.share_url),
    created_at: createdAt,
    description: optionalString(raw.description, "description", 1000),
    status: optionalString(raw.status, "status", 100),
    visibility,
    source: "user_manifest",
  };
}

export function parseCatalogueManifest(json: string | undefined): CatalogueManifest {
  if (!json) return {version: 1, entries: []};
  let value: unknown;
  try { value = JSON.parse(json); } catch { throw new Error("Catalogue manifest is not valid JSON"); }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Invalid catalogue manifest");
  }
  const raw = value as Record<string, unknown>;
  for (const key of Object.keys(raw)) {
    if (!["version", "owner_user_id", "entries"].includes(key)) {
      throw new Error(`Unsupported catalogue manifest field: ${key}`);
    }
  }
  if (raw.version !== 1 || !Array.isArray(raw.entries) || raw.entries.length > 1000) {
    throw new Error("Invalid catalogue manifest version or entry count");
  }
  const entries = raw.entries.map(validateEntry);
  const ownerUserId = optionalString(raw.owner_user_id, "owner_user_id", 200);
  if (entries.length && !ownerUserId) throw new Error("Catalogue owner_user_id is required");
  if (new Set(entries.map((entry) => entry.id)).size !== entries.length) {
    throw new Error("Duplicate catalogue id");
  }
  return {version: 1, ...(ownerUserId ? {owner_user_id: ownerUserId} : {}), entries};
}

export function listCatalogue(
  manifest: CatalogueManifest,
  args: Record<string, unknown> = {},
): {items: CatalogueEntry[]; total: number; next_cursor?: string} {
  for (const key of Object.keys(args)) {
    if (!["query", "limit", "cursor"].includes(key)) throw new Error(`Unsupported argument: ${key}`);
  }
  const query = args.query === undefined || args.query === "" ? "" : requiredString(args.query, "query", 200).toLocaleLowerCase();
  const limit = args.limit === undefined ? 50 : args.limit;
  if (!Number.isInteger(limit) || (limit as number) < 1 || (limit as number) > 100) {
    throw new Error("limit must be an integer from 1 to 100");
  }
  const cursorText = args.cursor === undefined ? "0" : requiredString(args.cursor, "cursor", 20);
  if (!/^\d+$/.test(cursorText)) throw new Error("Invalid cursor");
  const offset = Number(cursorText);
  if (!Number.isSafeInteger(offset)) throw new Error("Invalid cursor");
  const filtered = query ? manifest.entries.filter((entry) =>
    [entry.title, entry.creator, entry.description, entry.status]
      .some((field) => field?.toLocaleLowerCase().includes(query))) : manifest.entries;
  const items = filtered.slice(offset, offset + (limit as number));
  const next = offset + items.length;
  return {
    items,
    total: filtered.length,
    ...(next < filtered.length ? {next_cursor: String(next)} : {}),
  };
}
