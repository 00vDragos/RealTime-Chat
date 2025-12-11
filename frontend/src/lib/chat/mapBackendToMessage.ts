import type { BackendMessage } from "@/lib/api";
import type { Message } from "@/features/chat/types";
import { formatTime } from "./formatTime";

function hasTimestamp(ts: unknown): boolean {
  if (ts == null) return false;
  if (typeof ts === "string") return ts.length > 0;
  if (typeof ts === "object") return Object.keys(ts as Record<string, unknown>).length > 0;
  return false;
}

type ReadMapInfo = {
  entries: NonNullable<Message["seenBy"]>;
  latest: string | null;
};

function mapUserTimeMap(map: unknown, currentUserId: string): ReadMapInfo {
  if (!map || typeof map !== "object") {
    return { entries: [], latest: null };
  }

  const rawEntries: { userId: string; iso: string }[] = [];
  for (const [userId, value] of Object.entries(map as Record<string, unknown>)) {
    if (typeof value !== "string" || !value) continue;
    rawEntries.push({ userId, iso: value });
  }

  if (rawEntries.length === 0) {
    return { entries: [], latest: null };
  }

  rawEntries.sort((a, b) => new Date(a.iso).getTime() - new Date(b.iso).getTime());
  const latest = rawEntries[rawEntries.length - 1];

  const entries = rawEntries.map(({ userId, iso }) => ({
    userId,
    label: userId === currentUserId ? "You" : `User ${userId.slice(0, 8)}`,
    at: formatTime(iso),
  }));

  return {
    entries,
    latest: latest ? formatTime(latest.iso) : null,
  };
}

export function mapBackendToMessage(bm: BackendMessage, userId: string): Message {
  const deliveredInfo = mapUserTimeMap(bm.delivered_at, userId);
  const seenInfo = mapUserTimeMap(bm.seen_at, userId);
  const status: Message["status"] = bm.sender_id === userId
    ? (seenInfo.entries.length ? "seen" : deliveredInfo.entries.length ? "delivered" : "sent")
    : undefined;
  return {
    id: bm.id,
    sender: bm.sender_id === userId ? "Me" : (bm.sender_name || bm.sender_id),
    text: bm.body,
    time: formatTime(bm.created_at),
    isDeleted: bm.deleted_for_everyone,
    isEdited: hasTimestamp(bm.edited_at),
    status,
    deliveredAt: deliveredInfo.latest,
    seenAt: seenInfo.latest,
    deliveredBy: deliveredInfo.entries,
    seenBy: seenInfo.entries,
  };
}
