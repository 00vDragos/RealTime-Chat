import { useCallback, useEffect, useState } from "react";
import type { Chat } from "../features/chat/types";
import { listConversations, type ConversationSummary } from "../lib/api";
import { useAuthUserId } from "@/features/auth/useAuthSession";

function mapSummaryToChat(s: ConversationSummary, currentUserId?: string): Chat {
  // Build a display name: for groups (participantNames length > 2) exclude current user
  // and show up to 2 names, using "+N" truncation for long lists.
  let displayName = s.friendName ?? "";
  if (s.participantNames && s.participantIds && s.participantNames.length > 2) {
    const zipped = s.participantIds.map((id, idx) => ({ id, name: s.participantNames![idx] }))
      .filter(item => item && item.name);

    // Exclude current user if present
    let others = currentUserId ? zipped.filter(item => String(item.id) !== String(currentUserId)) : zipped;

    // If exclusion produced fewer than 2 names (unexpected), fallback to zipped list
    if (others.length < 2 && zipped.length >= 2) {
      others = zipped;
    }

    if (others.length > 0) {
      if (others.length <= 3) {
        displayName = others.map(o => o.name).join(', ');
      } else {
        const visible = others.slice(0, 3).map(o => o.name).join(', ');
        displayName = `${visible}, +${others.length - 3}`;
      }
    }
  }

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
      const mapped = data.map((s) => mapSummaryToChat(s, userId));
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
