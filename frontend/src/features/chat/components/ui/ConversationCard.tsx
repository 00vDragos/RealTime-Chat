import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import type { Chat } from "../../types";

type ConversationCardProps = {
    chat: Chat;
    selected: boolean;
    onClick: () => void;
};

export default function ConversationCard({ chat, selected, onClick }: ConversationCardProps) {
    return (
        <div
            onClick={onClick}
            className={`flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer border-b transition-colors ${selected ? 'bg-gray-100' : ''}`}
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
    );
}
