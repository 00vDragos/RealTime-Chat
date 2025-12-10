import { useCallback, useEffect, useMemo, useState } from "react";
import type { Message, Chat } from "../features/chat/types";
import {
  getMessages,
  sendMessage as apiSendMessage,
  editMessage as apiEditMessage,
  deleteMessage as apiDeleteMessage,
  updateLastRead,
} from "../lib/api";
import { mapBackendToMessage } from "@/lib/chat/mapBackendToMessage";
import { useAuthUserId } from "@/features/auth/useAuthSession";

export function useChatMessages(initialChats: Chat[]) {
  const [chatsState, setChatsState] = useState<Chat[]>(initialChats);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState("");
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const userId = useAuthUserId();

  const selectedChat = useMemo(() => chatsState.find((c) => c.id === selectedChatId) || null, [chatsState, selectedChatId]);

  // Keep local chats state in sync when conversations load/update (stable initialization)
  useEffect(() => {
    setChatsState(initialChats);
  }, [initialChats]);

  useEffect(() => {
    if (!selectedChatId || !userId) return;
    (async () => {
      try {
        const backendMessages = await getMessages(selectedChatId, userId);
        const mapped = backendMessages.map((m) => mapBackendToMessage(m, userId));
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: mapped } : c)));

        const lastOtherMsg = backendMessages
          .filter((m) => m.sender_id !== userId)
          .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
          .at(-1);
        if (lastOtherMsg) {
          await updateLastRead(selectedChatId, userId, lastOtherMsg.id);
          // Zero unread locally for the selected chat after marking last read
          setChatsState((prev) => prev.map((c) => (
            c.id === selectedChatId ? { ...c, unread: 0 } : c
          )));
        }
      } catch (e) {
        console.warn("Failed to fetch messages, using local data", e);
      }
    })();
  }, [selectedChatId, userId]);

  const handleEditStart = useCallback((msg: Message) => {
    setEditingMessageId(msg.id);
    setMessageInput(msg.text);
  }, []);

  const handleSend = useCallback(() => {
    if (!selectedChatId || !messageInput.trim() || !userId) return;
    const body = messageInput.trim();

    if (editingMessageId) {
      (async () => {
        try {
          const updated = await apiEditMessage(selectedChatId, editingMessageId, userId, body);
          const mapped = mapBackendToMessage(updated, userId);
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
        const created = await apiSendMessage(selectedChatId, userId, body);
        const newMsg = mapBackendToMessage(created, userId);
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
          return updated.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
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
          return updated.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        });
      } finally {
        setMessageInput("");
      }
    })();
  }, [selectedChatId, messageInput, editingMessageId, userId]);

  const handleDelete = useCallback((msg: Message) => {
    if (!selectedChatId || !userId) return;
    (async () => {
      try {
        await apiDeleteMessage(selectedChatId, msg.id, userId);
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
  }, [selectedChatId, userId]);

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
    handleDelete,
  } as const;
}
