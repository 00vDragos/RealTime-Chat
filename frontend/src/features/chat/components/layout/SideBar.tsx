import { useState } from 'react';
import type { Chat } from "../../types";
import { createConversation } from "@/lib/api";
import SideBarHeader from "./SideBarHeader";
import ConversationsList from "../ui/ConversationsList";

type SideBarProps = {
    chats: Chat[];
    selectedChatId: string | null;
    setSelectedChatId: (id: string) => void;
    onConversationCreated?: (conversation: any) => void;
};

export default function SideBar({ chats, selectedChatId, setSelectedChatId, onConversationCreated }: SideBarProps) {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredChats = (chats ?? []).filter(chat => {
        const name = (chat?.name ?? '').toLowerCase();
        return name.includes(searchQuery.toLowerCase());
    });

    // Handler for starting a new chat with multiple contacts
    const handleStartChat = async (contactIds: (number | string)[]) => {
        try {
            if (!contactIds.length) return;
            // Create a conversation with selected participant IDs (strings)
            const participantIds = contactIds.map(String);
            const res = await createConversation(participantIds);
            // Expect backend to return conversation info; if only 201/no body, you may need to refetch list
            if (onConversationCreated) {
                onConversationCreated(res);
            }
            // Select the newly created conversation by its id
            const newId = (res as any)?.id ?? null;
            if (newId) setSelectedChatId(String(newId));
        } catch (e) {
            console.warn("Failed to create conversation", e);
        }
    };

    return (
        <div
            className="h-screen bg-[rgb(var(--background))] border-r flex flex-col overflow-y-auto"
            style={{ flexBasis: '25%', minWidth: 280, maxWidth: 400 }}
        >
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