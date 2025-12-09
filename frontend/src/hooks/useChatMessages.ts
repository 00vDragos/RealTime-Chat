import { useCallback, useEffect, useMemo, useState } from "react";
import type { Message, Chat } from "../features/chat/types";
import {
  getMessages,
  sendMessage as apiSendMessage,
  editMessage as apiEditMessage,
  deleteMessage as apiDeleteMessage,
  updateLastRead,
  type BackendMessage,
} from "../lib/api";

const USER_ID = "1eb0fa76-fad3-4dd2-9536-ec257c29bba3";

function formatTime(iso: string) {
  const d = new Date(iso);
  return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
}

function mapBackendToMessage(bm: BackendMessage, userId: string): Message {
  return {
    id: bm.id,
    // Show name for others; keep "Me" for own messages to preserve UI logic
    sender: bm.sender_id === userId ? "Me" : (bm.sender_name || bm.sender_id),
    text: bm.body,
    time: formatTime(bm.created_at),
    isDeleted: bm.deleted_for_everyone,
  };
}

export function useChatMessages(initialChats: Chat[]) {
  const [chatsState, setChatsState] = useState<Chat[]>(initialChats);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState("");
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);

  const selectedChat = useMemo(() => chatsState.find((c) => c.id === selectedChatId) || null, [chatsState, selectedChatId]);

  // Keep local chats state in sync when conversations load/update (stable initialization)
  useEffect(() => {
    setChatsState(initialChats);
  }, [initialChats]);

  useEffect(() => {
    if (!selectedChatId) return;
    (async () => {
      try {
        const backendMessages = await getMessages(selectedChatId, USER_ID);
        const mapped = backendMessages.map((m) => mapBackendToMessage(m, USER_ID));
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: mapped } : c)));

        const lastOtherMsg = backendMessages
          .filter((m) => m.sender_id !== USER_ID)
          .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
          .at(-1);
        if (lastOtherMsg) {
          await updateLastRead(selectedChatId, USER_ID, lastOtherMsg.id);
        }
      } catch (e) {
        console.warn("Failed to fetch messages, using local data", e);
      }
    })();
  }, [selectedChatId]);

  const handleEditStart = useCallback((msg: Message) => {
    setEditingMessageId(msg.id);
    setMessageInput(msg.text);
  }, []);

  const handleSend = useCallback(() => {
    if (!selectedChatId || !messageInput.trim()) return;
    const body = messageInput.trim();

    if (editingMessageId) {
      (async () => {
        try {
          const updated = await apiEditMessage(selectedChatId, editingMessageId, USER_ID, body);
          const mapped = mapBackendToMessage(updated, USER_ID);
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
        const created = await apiSendMessage(selectedChatId, USER_ID, body);
        const newMsg = mapBackendToMessage(created, USER_ID);
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: [...c.messages, newMsg] } : c)));
      } catch (e) {
        console.warn("Failed to send to backend, appending locally", e);
        const nowIso = new Date().toISOString();
        const localMsg: Message = { id: crypto.randomUUID(), sender: "Me", text: body, time: formatTime(nowIso) };
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: [...c.messages, localMsg] } : c)));
      } finally {
        setMessageInput("");
      }
    })();
  }, [selectedChatId, messageInput, editingMessageId]);

  const handleDelete = useCallback((msg: Message) => {
    if (!selectedChatId) return;
    (async () => {
      try {
        await apiDeleteMessage(selectedChatId, msg.id, USER_ID);
        setChatsState((prev) => prev.map((c) => (c.id === selectedChatId ? { ...c, messages: c.messages.filter((m) => m.id !== msg.id) } : c)));
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
  }, [selectedChatId]);

  return {
    USER_ID,
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
