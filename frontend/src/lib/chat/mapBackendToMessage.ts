import type { BackendMessage } from "@/lib/api";
import type { Message } from "@/features/chat/types";
import { formatTime } from "./formatTime";

export function mapBackendToMessage(bm: BackendMessage, userId: string): Message {
  return {
    id: bm.id,
    sender: bm.sender_id === userId ? "Me" : (bm.sender_name || bm.sender_id),
    text: bm.body,
    time: formatTime(bm.created_at),
    isDeleted: bm.deleted_for_everyone,
    isEdited: !!bm.edited_at,
  };
}
