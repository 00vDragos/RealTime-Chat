const envWsBase = import.meta.env.VITE_WS_URL as string | undefined;
const envApiBase = import.meta.env.VITE_API_URL as string | undefined;

function normalizeBaseUrl(raw?: string | null) {
  if (!raw) return null;
  const trimmed = raw.trim();
  if (!trimmed) return null;
  try {
    const url = new URL(trimmed);
    if (!envWsBase) {
      url.pathname = '';
      url.search = '';
      url.hash = '';
    }
    if (url.protocol === 'http:') {
      url.protocol = 'ws:';
    } else if (url.protocol === 'https:') {
      url.protocol = 'wss:';
    }
    return url.toString().replace(/\/$/, '');
  } catch (error) {
    return trimmed.replace(/\/$/, '');
  }
}

const derivedWsBase = normalizeBaseUrl(envWsBase ?? envApiBase);

export function getChatWebSocketUrl(userId: string): string | null {
  if (!userId) return null;
  if (!derivedWsBase) {
    console.warn('Missing VITE_WS_URL or VITE_API_URL. Cannot open chat websocket.');
    return null;
  }
  return `${derivedWsBase}/ws/${userId}`;
}

export type TypingEvent = 'typing_start' | 'typing_stop';

export type ChatInboundMessage = {
  id: string;
  body: string;
  sender_id: string;
  sender_name?: string;
};

export type ChatInboundEvent =
  | { event: 'new_message'; conversation_id: string; message: ChatInboundMessage }
  | { event: 'message_edited'; conversation_id: string; message: ChatInboundMessage }
  | { event: 'message_deleted'; conversation_id: string; message_id: string; deleted_by?: string; deletor_name?: string }
  | { event: 'message_read'; conversation_id: string; message_id: string; user_id: string; user_name?: string }
  | { event: TypingEvent; conversation_id: string; user_id: string; sender_name?: string }
  | { event: string; [key: string]: unknown };

export type ChatOutboundEvent = { event: TypingEvent; conversation_id: string };

export function isTypingEvent(event: ChatInboundEvent): event is Extract<ChatInboundEvent, { event: TypingEvent }> {
  return event.event === 'typing_start' || event.event === 'typing_stop';
}
