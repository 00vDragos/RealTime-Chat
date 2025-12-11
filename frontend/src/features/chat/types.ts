export type MessageReadEntry = {
  userId: string;
  label: string;
  at: string;
};

export type MessageReaction = {
  emoji: string;
  count: number;
  reactedByMe: boolean;
};

export type Message = {
  id: string;
  text: string;
  sender: string;
  time: string;
  isDeleted?: boolean;
  isEdited?: boolean;
  status?: "sent" | "delivered" | "seen";
  deliveredAt?: string | null;
  seenAt?: string | null;
   deliveredBy?: MessageReadEntry[];
   seenBy?: MessageReadEntry[];
  reactions?: Record<string, string[]>;
  reactionSummary?: MessageReaction[];
};

export type Chat = {
  id: string;
  friendId?: string | null;
  name: string;
  avatar: string | null;
  lastMessage: string;
  timestamp: string;
  unread: number;
  messages: Message[];
  isBot?: boolean;
  isOnline?: boolean;
  lastSeen?: string | null;
  participantIds?: string[];
  participantNames?: string[];
};

