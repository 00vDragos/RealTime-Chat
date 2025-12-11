import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import type { Chat } from "../../types";
import { formatConversationTimestamp } from "@/lib/utils";

type ConversationCardProps = {
    chat: Chat;
    selected: boolean;
    onClick: () => void;
};

export default function ConversationCard({ chat, selected, onClick }: ConversationCardProps) {
    return (
        <div
            onClick={onClick}
            className={`flex items-center px-4 py-3 cursor-pointer border-b transition-colors
                ${selected ? 'bg-[rgb(var(--sidebar))]' : ''}
                hover:bg-[rgb(var(--muted))]`
            }
        >
            {/* Avatar */}
            <div className="relative">
                <Avatar className="h-12 w-12">
                    {chat.avatar && (
                        <AvatarImage src={chat.avatar} alt={chat.name} />
                    )}
                    <AvatarFallback className="bg-[rgb(var(--destructive))] text-[rgb(var(--foreground))]">
                        {chat.name?.trim().charAt(0)?.toUpperCase() || "?"}
                    </AvatarFallback>
                </Avatar>
                <span
                    className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-[rgb(var(--background))] ${
                      chat.isOnline ? 'bg-emerald-500' : 'bg-[rgb(var(--muted-foreground))]'
                    }`}
                    aria-label={chat.isOnline ? 'Online' : 'Offline'}
                  />
            </div>

            {/* Chat Info */}
            <div className="flex-1 ml-3 min-w-0">
                <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-[rgb(var(--foreground))] truncate">
                        {chat.name}
                    </h3>
                    <span className="text-xs text-[rgb(var(--muted-foreground))] ml-2">
                        {formatConversationTimestamp(chat.timestamp)}
                    </span>
                </div>
                <div className="flex items-center justify-between">
                    <p className="text-sm text-[rgb(var(--muted-foreground))] truncate">
                        {chat.lastMessage}
                    </p>
                    {chat.unread > 0 && (
                        <Badge className="ml-2 bg-[rgb(var(--primary))] hover:bg-[rgb(var(--primary))]/80 text-[rgb(var(--primary-foreground))]">
                            {chat.unread}
                        </Badge>
                    )}
                
                </div>
            </div>
        </div>
    );
}
