import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Message, Chat } from "../features/chat/types";
import {
  getMessages,
  sendMessage as apiSendMessage,
  editMessage as apiEditMessage,
  deleteMessage as apiDeleteMessage,
  updateLastRead,
  addMessageReaction as apiAddMessageReaction,
  changeMessageReaction as apiChangeMessageReaction,
  removeMessageReaction as apiRemoveMessageReaction,
} from "../lib/api";
import { mapBackendToMessage, deriveReactionState } from "@/lib/chat/mapBackendToMessage";
import { useAuthUserId } from "@/features/auth/useAuthSession";
import { useChatWebSocket } from "./useChatWebSocket";
import type { ChatInboundEvent, ChatInboundMessage } from "@/lib/chat/realtime";

type TypingEntry = { userId: string; userName?: string };

function sortChatsByTimestamp(chats: Chat[]) {
  return [...chats].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}

export function useChatMessages(initialChats: Chat[]) {
  const [chatsState, setChatsState] = useState<Chat[]>(initialChats);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState("");
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [typingMap, setTypingMap] = useState<Record<string, TypingEntry[]>>({});
  const authUserId = useAuthUserId();

  const typingStateRef = useRef<"idle" | "typing">("idle");
  const typingConversationRef = useRef<string | null>(null);
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const selectedChat = useMemo(() => chatsState.find((c) => c.id === selectedChatId) || null, [chatsState, selectedChatId]);
  const typingParticipants = selectedChatId ? typingMap[selectedChatId] ?? [] : [];

  const synchronizeConversationMessages = useCallback(async (conversationId: string, opts: { bumpUnread?: boolean } = {}) => {
    if (!authUserId) return;
    try {
      const backendMessages = await getMessages(conversationId, authUserId);
      const mapped = backendMessages.map((m) => mapBackendToMessage(m, authUserId));
      const latest = backendMessages.at(-1);
      setChatsState((prev) => {
        let found = false;
        const updated = prev.map((chat) => {
          if (chat.id !== conversationId) return chat;
          found = true;
          const shouldZeroUnread = conversationId === selectedChatId;
          const nextUnread = shouldZeroUnread
            ? 0
            : opts.bumpUnread
            ? chat.unread + 1
            : chat.unread;
          return {
            ...chat,
            messages: mapped,
            lastMessage: latest?.body ?? chat.lastMessage,
            timestamp: latest?.created_at ?? chat.timestamp,
            unread: nextUnread,
          };
        });
        if (!found) {
          return prev;
        }
        return sortChatsByTimestamp(updated);
      });
    } catch (error) {
      console.warn("Failed to sync conversation via realtime event", error);
    }
  }, [authUserId, selectedChatId]);

  const updateTypingIndicator = useCallback((conversationId?: string, userId?: string, userName?: string, isTyping = false) => {
    if (!conversationId || !userId || userId === authUserId) return;
    setTypingMap((prev) => {
      const current = prev[conversationId] ?? [];
      const existingIndex = current.findIndex((entry) => entry.userId === userId);
      let nextList = current;

      if (isTyping) {
        if (existingIndex >= 0) {
          nextList = current.map((entry, idx) => (idx === existingIndex ? { userId, userName } : entry));
        } else {
          nextList = [...current, { userId, userName }];
        }
      } else if (existingIndex >= 0) {
        nextList = current.filter((entry) => entry.userId !== userId);
      }

      if (nextList === current) {
        return prev;
      }

      const clone = { ...prev };
      if (nextList.length === 0) {
        delete clone[conversationId];
      } else {
        clone[conversationId] = nextList;
      }
      return clone;
    });
  }, [authUserId]);

  const handleRealtimeEvent = useCallback((payload: ChatInboundEvent) => {
    if (!payload || typeof payload.event !== "string") return;
    const conversationId: string | undefined =
      "conversation_id" in payload && typeof payload.conversation_id === "string"
        ? payload.conversation_id
        : undefined;

    switch (payload.event) {
      case "new_message": {
        if (typeof conversationId !== "string") return;
        const targetConversationId = conversationId;
        synchronizeConversationMessages(targetConversationId, { bumpUnread: targetConversationId !== selectedChatId });
        const inboundMessage = payload.message as ChatInboundMessage | undefined;
        if (
          targetConversationId === selectedChatId &&
          authUserId &&
          inboundMessage?.id &&
          inboundMessage.sender_id !== authUserId
        ) {
          (async () => {
            try {
              await updateLastRead(targetConversationId, authUserId, inboundMessage.id);
            } catch (error) {
              console.warn("Failed to mark message as read in realtime handler", error);
            }
          })();
        }
        break;
      }
      case "message_edited": {
        if (typeof conversationId !== "string" || !payload.message) return;
        const inboundMessage = payload.message as ChatInboundMessage | undefined;
        if (!inboundMessage) return;
        setChatsState((prev) => {
          let touched = false;
          const next = prev.map((chat) => {
            if (chat.id !== conversationId) return chat;
            let messageTouched = false;
            const updatedMessages = chat.messages.map((msg) => {
              if (msg.id !== inboundMessage.id) return msg;
              messageTouched = true;
              return { ...msg, text: inboundMessage.body, isEdited: true };
            });
            if (!messageTouched) return chat;
            touched = true;
            const isLast = chat.messages.at(-1)?.id === inboundMessage.id;
            return {
              ...chat,
              messages: updatedMessages,
              lastMessage: isLast ? inboundMessage.body : chat.lastMessage,
            };
          });
          return touched ? next : prev;
        });
        break;
      }
      case "message_deleted": {
        if (typeof conversationId !== "string" || typeof payload.message_id !== "string") return;
        setChatsState((prev) => {
          let touched = false;
          const next = prev.map((chat) => {
            if (chat.id !== conversationId) return chat;
            let messageTouched = false;
            const updatedMessages = chat.messages.map((msg) => {
              if (msg.id !== payload.message_id) return msg;
              messageTouched = true;
              return { ...msg, isDeleted: true, text: "" };
            });
            if (!messageTouched) return chat;
            touched = true;
            const remaining = [...updatedMessages].reverse().find((msg) => !msg.isDeleted && msg.text.trim().length > 0);
            return {
              ...chat,
              messages: updatedMessages,
              lastMessage: remaining?.text ?? "",
            };
          });
          return touched ? next : prev;
        });
        break;
      }
      case "message_read": {
        if (typeof conversationId !== "string") return;
        const readerId = typeof payload.user_id === "string" ? payload.user_id : undefined;
        if (!readerId || readerId === authUserId) return;
        const baseIds = Array.isArray(payload.message_ids)
          ? payload.message_ids.filter((id): id is string => typeof id === "string")
          : [];
        if (typeof payload.message_id === "string" && !baseIds.includes(payload.message_id)) {
          baseIds.push(payload.message_id);
        }
        if (baseIds.length === 0) return;
        const idsToUpdate = new Set(baseIds);
        setChatsState((prev) => {
          let touched = false;
          const next = prev.map((chat) => {
            if (chat.id !== conversationId) return chat;
            let messageTouched = false;
            const updatedMessages = chat.messages.map((msg): Message => {
              if (!idsToUpdate.has(msg.id) || msg.sender !== "Me" || msg.status === "seen") return msg;
              messageTouched = true;
              return { ...msg, status: "seen" };
            });
            if (!messageTouched) return chat;
            touched = true;
            return { ...chat, messages: updatedMessages };
          });
          return touched ? next : prev;
        });
        // As a safety net, re-sync this conversation from the backend
        // so local state (including status flags) matches the DB.
        void synchronizeConversationMessages(conversationId);
        break;
      }
      case "message_reaction_updated": {
        if (!authUserId || typeof conversationId !== "string" || typeof payload.message_id !== "string") {
          return;
        }
        const reactionState = deriveReactionState(payload.reactions, authUserId);
        const normalized = Object.keys(reactionState.normalized).length ? reactionState.normalized : undefined;
        const summary = reactionState.summary.length ? reactionState.summary : undefined;
        setChatsState((prev) => {
          let touched = false;
          const next = prev.map((chat) => {
            if (chat.id !== conversationId) return chat;
            let messageTouched = false;
            const updatedMessages = chat.messages.map((msg) => {
              if (msg.id !== payload.message_id) return msg;
              messageTouched = true;
              return {
                ...msg,
                reactions: normalized,
                reactionSummary: summary,
              };
            });
            if (!messageTouched) return chat;
            touched = true;
            return { ...chat, messages: updatedMessages };
          });
          return touched ? next : prev;
        });
        break;
      }
      case "presence_update": {
        const targetUserId = typeof payload.user_id === "string" ? payload.user_id : null;
        if (!targetUserId) return;
        const isOnline = Boolean((payload as { is_online?: unknown }).is_online);
        const rawLastSeen = (payload as { last_seen?: unknown }).last_seen;
        const lastSeen = typeof rawLastSeen === "string" ? rawLastSeen : null;
        setChatsState((prev) => {
          let touched = false;
          const next = prev.map((chat) => {
            if (chat.friendId !== targetUserId) return chat;
            touched = true;
            return {
              ...chat,
              isOnline,
              lastSeen: isOnline ? chat.lastSeen : lastSeen ?? chat.lastSeen,
            };
          });
          return touched ? next : prev;
        });
        break;
      }
      case "typing_start": {
        updateTypingIndicator(
          conversationId,
          typeof payload.user_id === "string" ? payload.user_id : undefined,
          typeof payload.sender_name === "string" ? payload.sender_name : undefined,
          true,
        );
        break;
      }
      case "typing_stop": {
        updateTypingIndicator(
          conversationId,
          typeof payload.user_id === "string" ? payload.user_id : undefined,
          typeof payload.sender_name === "string" ? payload.sender_name : undefined,
          false,
        );
        break;
      }
      default:
        break;
    }
  }, [authUserId, selectedChatId, synchronizeConversationMessages, updateTypingIndicator]);

  const { send: sendRealtimeEvent } = useChatWebSocket(authUserId, {
    enabled: Boolean(authUserId),
    onEvent: handleRealtimeEvent,
  });

  const emitTypingStop = useCallback(() => {
    if (typingStateRef.current !== "typing") {
      typingConversationRef.current = null;
      return;
    }
    const conversationId = typingConversationRef.current;
    if (conversationId) {
      sendRealtimeEvent({ event: "typing_stop", conversation_id: conversationId });
    }
    typingStateRef.current = "idle";
    typingConversationRef.current = null;
  }, [sendRealtimeEvent]);

  // Keep local chats state in sync when conversations load/update (stable initialization)
  useEffect(() => {
    setChatsState(initialChats);
  }, [initialChats]);

  useEffect(() => {
    if (!selectedChatId || !authUserId) return;
    (async () => {
      try {
        const backendMessages = await getMessages(selectedChatId, authUserId);
        const mapped = backendMessages.map((m) => mapBackendToMessage(m, authUserId));
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: mapped } : c)));

        const lastOtherMsg = backendMessages
          .filter((m) => m.sender_id !== authUserId)
          .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
          .at(-1);
        if (lastOtherMsg) {
          await updateLastRead(selectedChatId, authUserId, lastOtherMsg.id);
          // Zero unread locally for the selected chat after marking last read
          setChatsState((prev) => prev.map((c) => (
            c.id === selectedChatId ? { ...c, unread: 0 } : c
          )));
        }
      } catch (e) {
        console.warn("Failed to fetch messages, using local data", e);
      }
    })();
  }, [selectedChatId, authUserId]);

  useEffect(() => {
    if (!selectedChatId) {
      emitTypingStop();
      return;
    }

    if (typingConversationRef.current && typingConversationRef.current !== selectedChatId) {
      emitTypingStop();
    }

    const hasContent = messageInput.trim().length > 0;
    if (hasContent && typingStateRef.current === "idle") {
      sendRealtimeEvent({ event: "typing_start", conversation_id: selectedChatId });
      typingStateRef.current = "typing";
      typingConversationRef.current = selectedChatId;
    } else if (!hasContent) {
      emitTypingStop();
    }

    if (hasContent) {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      typingTimeoutRef.current = setTimeout(() => {
        emitTypingStop();
      }, 3000);
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = null;
      }
    };
  }, [messageInput, selectedChatId, emitTypingStop, sendRealtimeEvent]);

  useEffect(() => {
    return () => {
      emitTypingStop();
    };
  }, [emitTypingStop]);

  const handleEditStart = useCallback((msg: Message) => {
    setEditingMessageId(msg.id);
    setMessageInput(msg.text);
  }, []);

  const handleSend = useCallback(() => {
    if (!selectedChatId || !messageInput.trim() || !authUserId) return;
    const body = messageInput.trim();

    if (editingMessageId) {
      (async () => {
        try {
          const updated = await apiEditMessage(selectedChatId, editingMessageId, authUserId, body);
          const mapped = mapBackendToMessage(updated, authUserId);
          setChatsState((prev) =>
            prev.map((c) =>
              c.id === selectedChatId
                ? { ...c, messages: c.messages.map((m) => (m.id === editingMessageId ? { ...mapped } : m)) }
                : c
            )
          );
        } catch (e) {
          console.warn("Failed to edit via backend, updating locally", e);
          setChatsState((prev) =>
            prev.map((c) =>
              c.id === selectedChatId
                ? { ...c, messages: c.messages.map((m) => (m.id === editingMessageId ? { ...m, text: body } : m)) }
                : c
            )
          );
        } finally {
          setEditingMessageId(null);
          setMessageInput("");
        }
      })();
      return;
    }

    (async () => {
      try {
        const created = await apiSendMessage(selectedChatId, authUserId, body);
        const newMsg = mapBackendToMessage(created, authUserId);
        setChatsState((prev) => {
          const updated = prev.map((c) => (
            c.id === selectedChatId
              ? {
                  ...c,
                  messages: [...c.messages, newMsg],
                  lastMessage: created.body ?? body,
                  timestamp: created.created_at ?? new Date().toISOString(),
                }
              : c
          ));
          return sortChatsByTimestamp(updated);
        });
      } catch (e) {
        console.warn("Failed to send to backend, appending locally", e);
        const nowIso = new Date().toISOString();
        const hh = new Date(nowIso).getHours().toString().padStart(2, "0");
        const mm = new Date(nowIso).getMinutes().toString().padStart(2, "0");
        const localMsg: Message = { id: crypto.randomUUID(), sender: "Me", text: body, time: `${hh}:${mm}` };
        setChatsState((prev) => {
          const updated = prev.map((c) => (
            c.id === selectedChatId
              ? { ...c, messages: [...c.messages, localMsg], lastMessage: body, timestamp: nowIso }
              : c
          ));
          return sortChatsByTimestamp(updated);
        });
      } finally {
        setMessageInput("");
      }
    })();
  }, [selectedChatId, messageInput, editingMessageId, authUserId]);

  const handleReaction = useCallback((msg: Message, emoji: string) => {
    if (!authUserId || !emoji) return;
    const existingReaction = msg.reactionSummary?.find((entry) => entry.reactedByMe)?.emoji ?? null;

    (async () => {
      try {
        let updated;
        if (existingReaction && existingReaction === emoji) {
          updated = await apiRemoveMessageReaction(msg.id, emoji);
        } else if (existingReaction && existingReaction !== emoji) {
          updated = await apiChangeMessageReaction(msg.id, emoji);
        } else {
          updated = await apiAddMessageReaction(msg.id, emoji);
        }

        const mapped = mapBackendToMessage(updated, authUserId);
        const conversationId = updated.conversation_id;
        setChatsState((prev) =>
          prev.map((chat) =>
            chat.id === conversationId
              ? { ...chat, messages: chat.messages.map((m) => (m.id === mapped.id ? mapped : m)) }
              : chat
          )
        );
      } catch (error) {
        console.warn("Failed to update reaction", error);
      }
    })();
  }, [authUserId]);

  const handleDelete = useCallback((msg: Message) => {
    if (!selectedChatId || !authUserId) return;
    (async () => {
      try {
        await apiDeleteMessage(selectedChatId, msg.id, authUserId);
        // Mark as deleted locally so UI shows the deleted label immediately
        setChatsState((prev) =>
          prev.map((c) =>
            c.id === selectedChatId
              ? { ...c, messages: c.messages.map((m) => (m.id === msg.id ? { ...m, isDeleted: true, text: "" } : m)) }
              : c
          )
        );
      } catch (e) {
        console.warn("Failed to delete via backend, marking locally", e);
        setChatsState((prev) =>
          prev.map((c) =>
            c.id === selectedChatId
              ? { ...c, messages: c.messages.map((m) => (m.id === msg.id ? { ...m, isDeleted: true, text: "" } : m)) }
              : c
          )
        );
      }
    })();
  }, [selectedChatId, authUserId]);

  return {
    chatsState,
    selectedChatId,
    setSelectedChatId,
    selectedChat,
    messageInput,
    setMessageInput,
    editingMessageId,
    setEditingMessageId,
    handleEditStart,
    handleSend,
    handleReaction,
    handleDelete,
    typingParticipants,
  } as const;
}
