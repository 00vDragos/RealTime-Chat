import { useState } from 'react';
import { Search, MoreVertical, MessageCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

const mockChats = [
  {
    id: 1,
    name: 'John Doe',
    lastMessage: 'Hey, how are you doing?',
    timestamp: '10:30 AM',
    unread: 2,
    avatar: 'JD'
  },
  {
    id: 2,
    name: 'Sarah Smith',
    lastMessage: 'See you tomorrow!',
    timestamp: '9:15 AM',
    unread: 0,
    avatar: 'SS'
  },
  {
    id: 3,
    name: 'Team Project',
    lastMessage: 'The deadline is next week',
    timestamp: 'Yesterday',
    unread: 5,
    avatar: 'TP'
  },
  {
    id: 4,
    name: 'Mom',
    lastMessage: "Don't forget to call me",
    timestamp: 'Yesterday',
    unread: 1,
    avatar: 'M'
  },
  {
    id: 5,
    name: 'Alex Johnson',
    lastMessage: 'Thanks for the help!',
    timestamp: 'Monday',
    unread: 0,
    avatar: 'AJ'
  },
  {
    id: 6,
    name: 'Work Group',
    lastMessage: 'Meeting at 3 PM',
    timestamp: 'Monday',
    unread: 0,
    avatar: 'WG'
  }
];

export default function SideBar() {
  const [selectedChat, setSelectedChat] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredChats = mockChats.filter(chat =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-screen bg-white border-r flex flex-col" style={{ flexBasis: '25%', minWidth: 280, maxWidth: 400 }}>
      {/* Header */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-xl font-semibold text-gray-800">Chats</h1>
          <div className="flex gap-2">
            <Button variant="ghost" size="icon">
              <MessageCircle className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-5 w-5" />
            </Button>
          </div>
        </div>
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search or start new chat"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>
      {/* Chat List */}
      <ScrollArea className="flex-1">
        {filteredChats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => setSelectedChat(chat.id)}
            className={`flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer border-b transition-colors ${
              selectedChat === chat.id ? 'bg-gray-100' : ''
            }`}
          >
            {/* Avatar */}
            <Avatar className="h-12 w-12">
              <AvatarFallback className="bg-gradient-to-br from-green-400 to-green-600 text-white">
                {chat.avatar}
              </AvatarFallback>
            </Avatar>
            {/* Chat Info */}
            <div className="flex-1 ml-3 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-gray-900 truncate">
                  {chat.name}
                </h3>
                <span className="text-xs text-gray-500 ml-2">
                  {chat.timestamp}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600 truncate">
                  {chat.lastMessage}
                </p>
                {chat.unread > 0 && (
                  <Badge className="ml-2 bg-green-500 hover:bg-green-600 text-white">
                    {chat.unread}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
}
