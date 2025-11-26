import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MessageCirclePlus } from "lucide-react";

import { contacts } from "../../mockData";

export default function NewChatDialog({ onSelect }: { onSelect: (contactIds: number[]) => void }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<number[]>([]);

  const filtered = contacts.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  const toggleSelect = (id: number) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter(cid => cid !== id) : [...prev, id]
    );
  };

  const handleStartChat = () => {
    if (selected.length > 0) {
      onSelect(selected);
      setOpen(false);
      setSelected([]);
      setSearch("");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>

      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Start new chat">
          <MessageCirclePlus className="h-5 w-5" />
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-md">

        <DialogHeader>
          <DialogTitle>Start a new chat</DialogTitle>
        </DialogHeader>

        <Input
          placeholder="Search contacts..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="mb-4"
        />
        <div className="flex flex-col gap-2 p-2 max-h-60 overflow-y-auto">
          {filtered.length === 0 && <div className="text-gray-400 text-center">No contacts found</div>}
          {filtered.map(contact => {
            const isSelected = selected.includes(contact.id);
            return (
              <Button
                key={contact.id}
                variant={isSelected ? "secondary" : "ghost"}
                className={`w-full flex items-center gap-3 justify-start ${isSelected ? 'ring-2 ring-green-500 ring-offset-2 ring-offset-white' : ''}`}
                onClick={() => toggleSelect(contact.id)}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  readOnly
                  className="mr-2 accent-green-500"
                  tabIndex={-1}
                  style={{ pointerEvents: 'none' }}
                />
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-gradient-to-br from-green-400 to-green-600 text-white">
                    {contact.avatar}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium text-gray-800">{contact.name}</span>
              </Button>
            );
          })}
        </div>

        <Button
          className="mt-4 w-full"
          disabled={selected.length === 0}
          onClick={handleStartChat}
        >
          Start Chat with {selected.length} contact{selected.length !== 1 ? 's' : ''}
        </Button>
        
      </DialogContent>
    </Dialog>
  );
}
