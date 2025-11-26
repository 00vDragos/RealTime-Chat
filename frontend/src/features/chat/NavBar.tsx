import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { MoreVertical, Search, MessageCircle} from 'lucide-react';

export default function NavBar() {
    return (
        <div className="flex items-center justify-between px-4 py-3 bg-white border-b h-16">
            {/* User Avatar */}
            <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-gradient-to-br from-green-400 to-green-600 text-white">
                        U
                    </AvatarFallback>
                </Avatar>
                <span className="font-semibold text-gray-800">Username</span>
            </div>
            {/* Actions */}
            <div className="flex gap-2">
                <Button variant="ghost" size="icon">
                    <Search className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon">
                    <MessageCircle className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon">
                    <MoreVertical className="h-5 w-5" />
                </Button>
            </div>
        </div>
    );
}
