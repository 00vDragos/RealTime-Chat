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

export const chats: Chat[] = [
  {
    id: 1,
    name: 'John Doe',
    avatar: 'JD',
    lastMessage: 'Hey, how are you doing?',
    timestamp: '10:30 AM',
    unread: 2,
    messages: [
      { id: 1, text: 'Hey, how are you?', sender: 'John', time: '10:30 AM' },
      { id: 2, text: 'I am good, thanks!', sender: 'Me', time: '10:31 AM' },
      { id: 3, text: 'What about you?', sender: 'Me', time: '10:32 AM' },
    ],
  },
  {
    id: 2,
    name: 'Sarah Smith',
    avatar: 'SS',
    lastMessage: 'See you tomorrow!',
    timestamp: '9:15 AM',
    unread: 0,
    messages: [
      { id: 1, text: 'See you tomorrow!', sender: 'Sarah', time: '9:15 AM' },
      { id: 2, text: 'Sure!', sender: 'Me', time: '9:16 AM' },
    ],
  },
  {
    id: 3,
    name: 'Team Project',
    avatar: 'TP',
    lastMessage: 'The deadline is next week',
    timestamp: 'Yesterday',
    unread: 5,
    messages: [
      { id: 1, text: 'The deadline is next week', sender: 'Team', time: 'Yesterday' },
      { id: 2, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 3, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 4, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 5, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 6, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 7, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 8, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 9, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
      { id: 10, text: 'Let’s finish it soon.', sender: 'Me', time: 'Yesterday' },
    ],
  },
];

// Example contacts list for new chat dialog
export const contacts = [
  { id: 101, name: "Alice Blue", avatar: "AB" },
  { id: 102, name: "Bob Green", avatar: "BG" },
  { id: 103, name: "Charlie Red", avatar: "CR" },
  { id: 104, name: "Diana Yellow", avatar: "DY" },
  { id: 105, name: "Diana Yellow", avatar: "DY" },
  { id: 106, name: "Diana Yellow", avatar: "DY" },
  { id: 107, name: "Diana Yellow", avatar: "DY" },
  { id: 108, name: "Diana Yellow", avatar: "DY" },
];

// Example incoming friend requests for ManageFriendshipDialog
export const initialFriendRequests = [
  { id: 1, email: "alice@example.com", name: "Alice Blue", avatar: "AB" },
  { id: 2, email: "bob@example.com", name: "Bob Green", avatar: "BG" },
];