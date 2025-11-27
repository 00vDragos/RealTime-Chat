import { Search, MoreVertical } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';
import NewChatDialog from "../dialogs/NewChatDialog";
import { ThemeSwitcher } from '@/theme/ThemeSwitcher';

type SideBarHeaderProps = {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onStartChat: (contactIds: number[]) => void;
};

export default function SideBarHeader({ searchQuery, setSearchQuery, onStartChat }: SideBarHeaderProps) {
  return (
    <div className="bg-[rgb(var(--background))] px-4 py-3 border-b">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-semibold text-[rgb(var(--foreground))]">Chats</h1>
        <div className="flex gap-2">
          <NewChatDialog onSelect={onStartChat} />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <ThemeSwitcher />
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem variant="destructive">Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[rgb(var(--muted-foreground))] h-4 w-4" />
        <Input
          type="text"
          placeholder="Search or start new chat"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 text-[rgb(var(--muted-foreground))] placeholder-[rgb(var(--muted-foreground))]"
        />
      </div>
    </div>
  );
}
