export type Message = {
  id: number;
  text: string;
  sender: string;
  time: string;
  // Marks the message as deleted; UI will show a placeholder
  isDeleted?: boolean;
};

export type Chat = {
  id: number;
  name: string;
  avatar: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  messages: Message[];
};
