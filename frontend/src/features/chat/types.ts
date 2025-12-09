export type Message = {
  id: string;
  text: string;
  sender: string;
  time: string;
  isDeleted?: boolean;
  isEdited?: boolean;
  status?: "sent" | "delivered" | "seen";
};

export type Chat = {
  id: string;
  name: string;
  avatar: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  messages: Message[];
};

