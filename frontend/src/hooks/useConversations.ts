import { useEffect, useState } from "react";
import type { Chat } from "../features/chat/types";
import { listConversations, type ConversationSummary } from "../lib/api";

function mapSummaryToChat(s: ConversationSummary): Chat {
  return {
    id: s.id,
    name: s.friendName ?? "",
    avatar: (s.friendName ?? "").trim().charAt(0).toUpperCase() || "?",
    lastMessage: s.lastMessage ?? "",
    timestamp: s.lastMessageTime ?? "",
    unread: s.unreadCount ?? 0,
    messages: [],
  };
}

export function useConversations(initial: Chat[] = []) {
  const [conversations, setConversations] = useState<Chat[]>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listConversations();
      const mapped = data.map(mapSummaryToChat);
      setConversations(mapped);
    } catch (e: any) {
      console.warn("Failed to list conversations, keeping existing", e);
      setError(e?.message ?? "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refetch(); }, []);

  return { conversations, setConversations, loading, error, refetch } as const;
}
