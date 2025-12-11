import { useCallback, useEffect, useState } from "react";
import type { Chat } from "../features/chat/types";
import { listConversations, type ConversationSummary } from "../lib/api";
import { useAuthUserId } from "@/features/auth/useAuthSession";

function mapSummaryToChat(s: ConversationSummary): Chat {
  return {
    id: s.id,
    friendId: s.friendId ?? null,
    name: s.friendName ?? "",
    avatar: s.friendAvatar ?? null,
    lastMessage: s.lastMessage ?? "",
    timestamp: s.lastMessageTime ?? "",
    unread: s.unreadCount ?? 0,
    messages: [],
    isBot: s.friendProvider === "openai",
    isOnline: s.friendIsOnline ?? false,
    lastSeen: s.friendLastSeen ?? null,
  };
}

export function useConversations(initial: Chat[] = []) {
  const [conversations, setConversations] = useState<Chat[]>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const userId = useAuthUserId();

  const refetch = useCallback(async () => {
    if (!userId) {
      setConversations([]);
      setError("You must be signed in to load conversations");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await listConversations(userId);
      const mapped = data.map(mapSummaryToChat);
      setConversations(mapped);
    } catch (e: any) {
      console.warn("Failed to list conversations, keeping existing", e);
      setError(e?.message ?? "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      return;
    }
    refetch();
  }, [userId, refetch]);

  return { conversations, setConversations, loading, error, refetch } as const;
}
