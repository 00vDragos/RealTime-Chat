import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { MoreVertical, Search, MessageCircle} from 'lucide-react';

export default function NavBar() {
    return (
        <div className="flex items-center justify-between px-4 py-3 bg-[rgb(var(--background))] border-b h-16">
            {/* User Avatar */}
            <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-[rgb(var(--destructive))] text-white">
                        U
                    </AvatarFallback>
                </Avatar>
                <span className="font-semibold text-[rgb(var(--foreground))]">Username</span>
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
