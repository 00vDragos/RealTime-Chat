import { useState } from 'react';
import type { Chat } from "../../mockData";
import SideBarHeader from "./SideBarHeader";
import ConversationsList from "../ui/ConversationsList";

type SideBarProps = {
    chats: Chat[];
    selectedChatId: number | null;
    setSelectedChatId: (id: number) => void;
};

export default function SideBar({ chats, selectedChatId, setSelectedChatId }: SideBarProps) {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredChats = chats.filter(chat =>
        chat.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Handler for starting a new chat with multiple contacts
    const handleStartChat = (contactIds: number[]) => {
        if (contactIds.length > 0) {
            setSelectedChatId(contactIds[0]);
        }
        // TODO: Add logic to create a new chat with all selected contacts
    };

    return (
        <div className="h-screen bg-white border-r flex flex-col" style={{ flexBasis: '25%', minWidth: 280, maxWidth: 400 }}>
            {/* Header */}
            <SideBarHeader
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onStartChat={handleStartChat}
            />

            {/* Conversations List */}
            <ConversationsList
                chats={filteredChats}
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
            />
        </div>
    );
}