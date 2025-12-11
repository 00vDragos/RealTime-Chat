import { getStoredAccessToken } from '@/features/auth/storage';

const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  const accessToken = getStoredAccessToken();
  const headers = new Headers(init.headers || {});
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  const res = await fetch(url, {
    ...init,
    headers,
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
  sender_name?: string;
  body: string;
  created_at: string; // ISO
  delivered_at?: Record<string, unknown> | null;
  seen_at?: Record<string, unknown> | null;
  edited_at?: string | null;
  deleted_for_everyone: boolean;
  reactions?: Record<string, string[]> | null;
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

export async function addMessageReaction(messageId: string, reactionType: string): Promise<BackendMessage> {
  return fetchJson<BackendMessage>(`/messages/${messageId}/reactions`, {
    method: 'POST',
    body: JSON.stringify({ reaction_type: reactionType }),
  });
}

export async function changeMessageReaction(messageId: string, reactionType: string): Promise<BackendMessage> {
  return fetchJson<BackendMessage>(`/messages/${messageId}/reactions`, {
    method: 'PUT',
    body: JSON.stringify({ reaction_type: reactionType }),
  });
}

export async function removeMessageReaction(messageId: string, reactionType: string): Promise<BackendMessage> {
  return fetchJson<BackendMessage>(`/messages/${messageId}/reactions/${encodeURIComponent(reactionType)}`, {
    method: 'DELETE',
  });
}

export async function updateLastRead(conversationId: string, userId: string, messageId: string) {
  const params = new URLSearchParams({ message_id: messageId });
  return fetchJson(`/conversations/${conversationId}/read?${params.toString()}`, {
    method: 'POST',
    headers: { 'user-id': userId },
  });
}

// ------------------------------------------------------------------
// Conversations API
// ------------------------------------------------------------------
// Matches backend response from GET /api/messages/conversations
export type ConversationSummary = {
  id: string;
  friendId: string | null;
  friendName: string;
  participantIds?: string[];
  participantNames?: string[];
  friendAvatar?: string | null;
  friendProvider?: string | null;
  friendIsOnline?: boolean;
  friendLastSeen?: string | null;
  lastMessage: string | null;
  lastMessageTime: string | null; // ISO
  unreadCount: number;
};

export async function listConversations(userId: string): Promise<ConversationSummary[]> {
  // Endpoint defined with router prefix "/api/messages"
  return fetchJson<ConversationSummary[]>(`/api/messages/conversations`, {
    method: 'GET',
    headers: { 'user-id': userId },
  });
}

export async function createConversation(participantIds: string[], userId: string) {
  return fetchJson(`/api/messages/new_conversation`, {
    method: 'POST',
    headers: { 'user-id': userId },
    body: JSON.stringify({ participant_ids: participantIds }),
  });
}

export async function updateConversation(conversationId: string, payload: { title: string }) {
  return fetchJson(`/api/messages/conversations/${conversationId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteConversation(conversationId: string) {
  return fetchJson<{ detail: string }>(`/api/messages/conversations/${conversationId}`, {
    method: 'DELETE',
  });
}

// ------------------------------------------------------------------
// Friends API
// ------------------------------------------------------------------
export type Friend = {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string | null;
  provider?: string;
};

export async function listMyFriends(userId: string): Promise<Friend[]> {
  return fetchJson<Friend[]>(`/friends`, {
    method: 'GET',
    headers: { 'user-id': userId },
  });
}

export type FriendRequestUser = {
  id: string;
  email: string;
  display_name?: string | null;
  avatar_url?: string | null;
};

export type FriendRequest = {
  id: string;
  from_user_id: string;
  to_user_id: string;
  status: 'pending' | 'accepted' | 'declined' | 'canceled';
  created_at?: string;
  updated_at?: string;
  from_user?: FriendRequestUser | null;
  to_user?: FriendRequestUser | null;
};

export async function listFriendRequests(userId: string, direction?: 'in' | 'out'): Promise<FriendRequest[]> {
  const params = direction ? `?direction=${direction}` : '';
  return fetchJson<FriendRequest[]>(`/friends/requests${params}`, {
    method: 'GET',
    headers: { 'user-id': userId },
  });
}

export async function sendFriendRequest(toEmail: string, userId: string): Promise<FriendRequest> {
  return fetchJson<FriendRequest>(`/friends/requests`, {
    method: 'POST',
    headers: { 'user-id': userId },
    body: JSON.stringify({ to_email: toEmail }),
  });
}

export async function cancelFriendRequest(requestId: string, userId: string) {
  return fetchJson<{ detail: string }>(`/friends/requests/${requestId}`, {
    method: 'DELETE',
    headers: { 'user-id': userId },
  });
}

export async function respondToFriendRequest(
  requestId: string,
  status: 'accepted' | 'declined',
  userId: string,
): Promise<FriendRequest> {
  return fetchJson<FriendRequest>(`/friends/requests/${requestId}/respond`, {
    method: 'POST',
    headers: { 'user-id': userId },
    body: JSON.stringify({ status }),
  });
}

export async function removeFriend(friendId: string, userId: string) {
  return fetchJson<{ detail: string }>(`/friends/${friendId}`, {
    method: 'DELETE',
    headers: { 'user-id': userId },
  });
}
