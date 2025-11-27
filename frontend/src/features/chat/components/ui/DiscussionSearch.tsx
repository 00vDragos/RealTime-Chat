import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

export function DiscussionSearch() {

    const [searchQuery, setSearchQuery] = useState('');

    return (
         <div className="relative px-4">
            <Search className="absolute left-7 top-1/2 transform -translate-y-1/2 text-[rgb(var(--muted-foreground))] h-4 w-4" />
            <Input
              type="text"
              placeholder="Search or start new chat"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
    );
}

export default DiscussionSearch;