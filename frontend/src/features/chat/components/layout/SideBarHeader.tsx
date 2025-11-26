import { Search, MoreVertical } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import NewChatDialog from "../dialogs/NewChatDialog";

type SideBarHeaderProps = {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onStartChat: (contactIds: number[]) => void;
};

export default function SideBarHeader({ searchQuery, setSearchQuery, onStartChat }: SideBarHeaderProps) {
  return (
    <div className="bg-gray-50 px-4 py-3 border-b">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-semibold text-gray-800">Chats</h1>
        <div className="flex gap-2">
          <NewChatDialog onSelect={onStartChat} />
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
  );
}
