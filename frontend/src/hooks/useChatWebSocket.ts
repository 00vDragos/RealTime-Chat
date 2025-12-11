import { useCallback, useEffect, useRef, useState } from 'react';
import { getChatWebSocketUrl, type ChatInboundEvent, type ChatOutboundEvent } from '@/lib/chat/realtime';

type Status = 'idle' | 'connecting' | 'open' | 'error';

type Options = {
  enabled?: boolean;
  onEvent?: (event: ChatInboundEvent) => void;
};

export function useChatWebSocket(userId: string | null | undefined, options: Options = {}) {
  const { enabled = true, onEvent } = options;
  const [status, setStatus] = useState<Status>('idle');
  const handlerRef = useRef<Options['onEvent']>(undefined);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    handlerRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!enabled || !userId) {
      setStatus('idle');
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      return;
    }

    let stopped = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      const url = getChatWebSocketUrl(userId);
      if (!url || stopped) {
        return;
      }
      setStatus('connecting');
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        if (stopped) return;
        setStatus('open');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as ChatInboundEvent;
          handlerRef.current?.(data);
        } catch (error) {
          console.warn('[ws] failed to parse event', error);
        }
      };

      ws.onerror = () => {
        if (stopped) return;
        setStatus('error');
      };

      ws.onclose = () => {
        if (stopped) return;
        setStatus('error');
        reconnectTimer = setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [userId, enabled]);

  const send = useCallback((payload: ChatOutboundEvent) => {
    const ws = socketRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      return false;
    }
    ws.send(JSON.stringify(payload));
    return true;
  }, []);

  return { status, send };
}
