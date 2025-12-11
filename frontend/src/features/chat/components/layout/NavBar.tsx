import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { MoreVertical, Search, MessageCircle } from 'lucide-react';

type NavBarProps = {
    name?: string | null;
    avatar?: string | null;
};

export default function NavBar({ name, avatar }: NavBarProps) {
    const displayName = (name && name.trim().length > 0) ? name : 'Select a chat';
    const initial = (name || '')?.trim().charAt(0)?.toUpperCase() || 'U';
    return (
        <div className="flex items-center justify-between px-4 py-3 bg-[rgb(var(--background))] border-b h-16">
            {/* Conversation Avatar/Title */}
            <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                    {avatar && (
                        <AvatarImage src={avatar} alt={displayName} />
                    )}
                    <AvatarFallback className="bg-[rgb(var(--destructive))] text-white">
                        {initial}
                    </AvatarFallback>
                </Avatar>
                <span className="font-semibold text-[rgb(var(--foreground))]">{displayName}</span>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                <Button variant="ghost" size="icon">
                    <Search className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
                <Button variant="ghost" size="icon">
                    <MessageCircle className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
                <Button variant="ghost" size="icon">
                    <MoreVertical className="h-5 w-5 text-[rgb(var(--muted-foreground))]" />
                </Button>
            </div>
        </div>
    );
}
