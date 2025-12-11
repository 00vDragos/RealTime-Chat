import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { MoreVertical, Search, MessageCircle } from 'lucide-react';
import { formatLastSeen } from '@/lib/utils';

type NavBarProps = {
    name?: string | null;
    avatar?: string | null;
    isOnline?: boolean;
    lastSeen?: string | null;
    canEdit?: boolean;
    hasConversation?: boolean;
    onEditConversation?: () => void;
    onDeleteConversation?: () => void;
};

export default function NavBar({
    name,
    avatar,
    isOnline,
    lastSeen,
    canEdit,
    hasConversation,
    onEditConversation,
    onDeleteConversation,
}: NavBarProps) {
    const displayName = (name && name.trim().length > 0) ? name : 'Select a chat';
    const initial = displayName.trim().charAt(0).toUpperCase() || 'U';
    const presenceText = isOnline
        ? 'online'
        : lastSeen
        ? `last seen ${formatLastSeen(lastSeen)}`
        : '';
    const showActions = Boolean(hasConversation);
    return (
        <div className="flex items-center justify-between px-4 py-3 bg-[rgb(var(--background))] border-b h-16">
            {/* Conversation Avatar/Title */}
            <div className="flex items-center gap-3">
                <div className="relative">
                    <Avatar className="h-12 w-12">
                        {avatar && (
                            <AvatarImage src={avatar} alt={displayName} />
                        )}
                        <AvatarFallback className="bg-[rgb(var(--destructive))] text-white">
                            {initial}
                        </AvatarFallback>
                    </Avatar>
                    {presenceText && (
                        <span
                            className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-[rgb(var(--background))] ${
                                isOnline ? 'bg-emerald-500' : 'bg-[rgb(var(--muted-foreground))]'
                            }`}
                        />
                    )}
                </div>
                <div className="flex flex-col">
                    <span className="font-semibold text-[rgb(var(--foreground))]">{displayName}</span>
                    {presenceText && (
                        <span className="text-xs text-[rgb(var(--muted-foreground))]">{presenceText}</span>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                <Button variant="ghost" size="icon">
                    <Search className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
                <Button variant="ghost" size="icon">
                    <MessageCircle className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
                {showActions ? (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                                <MoreVertical className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="min-w-[12rem]">
                            {canEdit && (
                                <DropdownMenuItem
                                    onSelect={(event) => {
                                        event.preventDefault();
                                        onEditConversation?.();
                                    }}
                                >
                                    Edit conversation
                                </DropdownMenuItem>
                            )}
                            <DropdownMenuItem
                                variant="destructive"
                                onSelect={(event) => {
                                    event.preventDefault();
                                    onDeleteConversation?.();
                                }}
                            >
                                Delete conversation
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                ) : (
                    <Button variant="ghost" size="icon" disabled>
                        <MoreVertical className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                    </Button>
                )}
            </div>
        </div>
    );
}
