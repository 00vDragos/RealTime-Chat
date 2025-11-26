export type Message = {
  id: number;
  text: string;
  sender: string;
  time: string;
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
