import type { Message } from "../../types";
import { useRef, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Pencil, Trash2, Info, SmilePlus  } from "lucide-react";

type MessageBubbleProps = {
  message: Message;
  onEdit?: (msg: Message) => void;
};

export default function MessageBubble({ message, onEdit }: MessageBubbleProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setMenuOpen(true);
  };

  const handleEdit = () => {
    setMenuOpen(false);
    if (onEdit) onEdit(message);
  };

  const handleDelete = () => {
    setMenuOpen(false);
    // TODO: Implement delete logic
    alert("Delete message");
  };

  return (
    <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>

      <DropdownMenuTrigger asChild>
        <div
          ref={triggerRef}
          onContextMenu={handleContextMenu}
          className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${message.sender === 'Me' ? 'bg-[rgb(var(--primary-bright))]/10 self-end' : 'bg-[rgb(var(--background))] self-start'}`}
        >
          <div className="font-semibold text-xs text-[rgb(var(--muted-foreground))] mb-1">{message.sender}</div>
          <div className="text-[rgb(var(--foreground))]">{message.text}</div>
          <div className="text-xs text-[rgb(var(--muted-foreground))] mt-1 text-right">{message.time}</div>
        </div>
      </DropdownMenuTrigger>

      <DropdownMenuContent side="right" align="start">

        <DropdownMenuItem  className="flex items-center gap-2">
          <Info className="w-4 h-4 mr-2" /> Info
        </DropdownMenuItem>

        <DropdownMenuItem  className="flex items-center gap-2">
          <SmilePlus  className="w-4 h-4 mr-2" /> React
        </DropdownMenuItem>

        <DropdownMenuItem onClick={handleEdit} className="flex items-center gap-2">
          <Pencil className="w-4 h-4 mr-2" /> Edit
        </DropdownMenuItem>

        <DropdownMenuItem onClick={handleDelete} className="flex items-center gap-2 text-red-600 focus:text-red-600">
          <Trash2 className="w-4 h-4 mr-2" /> Delete
        </DropdownMenuItem>

      </DropdownMenuContent>

    </DropdownMenu>
  );
}
