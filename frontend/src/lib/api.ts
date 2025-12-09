const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
    credentials: init.credentials ?? 'include',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    // Log error responses uniformly
    console.log('[API ERROR]', {
      url,
      method: (init.method || 'GET'),
      status: res.status,
      statusText: res.statusText,
      body: text,
    });
    throw new Error(text || `Request failed: ${res.status}`);
  }
  const data = await res.json() as T;
  // Log successful responses uniformly
  console.log('[API OK]', {
    url,
    method: (init.method || 'GET'),
    status: res.status,
    data,
  });
  return data;
}

// ------------------------------------------------------------------
// Messages API
// ------------------------------------------------------------------
export type BackendMessage = {
  id: string;
  conversation_id: string;
  sender_id: string;
  body: string;
  created_at: string; // ISO
  delivered_at?: Record<string, unknown> | null;
  seen_at?: Record<string, unknown> | null;
  edited_at?: string | null;
  deleted_for_everyone: boolean;
};

export async function getMessages(conversationId: string, userId: string): Promise<BackendMessage[]> {
  return fetchJson<BackendMessage[]>(`/conversations/${conversationId}/messages`, {
    method: 'GET',
    headers: { 'user-id': userId },
  });
}

export async function sendMessage(conversationId: string, userId: string, body: string): Promise<BackendMessage> {
  const params = new URLSearchParams({ body });
  return fetchJson<BackendMessage>(`/conversations/${conversationId}/messages?${params.toString()}`, {
    method: 'POST',
    headers: { 'user-id': userId },
  });
}

export async function editMessage(conversationId: string, messageId: string, userId: string, newBody: string): Promise<BackendMessage> {
  const params = new URLSearchParams({ new_body: newBody });
  return fetchJson<BackendMessage>(`/conversations/${conversationId}/messages/${messageId}?${params.toString()}`, {
    method: 'PUT',
    headers: { 'user-id': userId },
  });
}

export type BackendMessageDeletion = {
  id: string;
  message_id: string;
  deleted_by_user_id: string;
  deleted_for_everyone: boolean;
  created_at: string;
};

export async function deleteMessage(conversationId: string, messageId: string, userId: string): Promise<BackendMessageDeletion> {
  return fetchJson<BackendMessageDeletion>(`/conversations/${conversationId}/messages/${messageId}` , {
    method: 'DELETE',
    headers: { 'user-id': userId },
  });
}

export async function updateLastRead(conversationId: string, userId: string, messageId: string) {
  const params = new URLSearchParams({ message_id: messageId });
  return fetchJson(`/conversations/${conversationId}/read?${params.toString()}`, {
    method: 'POST',
    headers: { 'user-id': userId },
  });
}
