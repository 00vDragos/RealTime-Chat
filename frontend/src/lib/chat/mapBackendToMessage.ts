import type { BackendMessage } from "@/lib/api";
import type { Message } from "@/features/chat/types";
import { formatTime } from "./formatTime";

function hasTimestamp(ts: unknown): boolean {
  if (ts == null) return false;
  if (typeof ts === "string") return ts.length > 0;
  if (typeof ts === "object") return Object.keys(ts as Record<string, unknown>).length > 0;
  return false;
}

export function mapBackendToMessage(bm: BackendMessage, userId: string): Message {
  const seen = hasTimestamp(bm.seen_at);
  const delivered = hasTimestamp(bm.delivered_at);
  const status: Message["status"] = bm.sender_id === userId
    ? (seen ? "seen" : delivered ? "delivered" : "sent")
    : undefined;
  return {
    id: bm.id,
    sender: bm.sender_id === userId ? "Me" : (bm.sender_name || bm.sender_id),
    text: bm.body,
    time: formatTime(bm.created_at),
    isDeleted: bm.deleted_for_everyone,
    isEdited: hasTimestamp(bm.edited_at),
    status,
  };
}
