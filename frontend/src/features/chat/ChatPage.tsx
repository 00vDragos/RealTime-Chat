import SideBar from "./components/layout/SideBar";
import { useState } from "react";
import { chats } from "./mockData";
import Navbar from "./components/layout/NavBar";
import MessagesList from "./components/ui/MessagesList";
import MessagesInput from "./components/ui/MessagesInput";
import type { Message } from "./types";

export default function ChatPage() {
    const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
    const [messageInput, setMessageInput] = useState("");
    const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
    const [chatState] = useState(chats);
    const selectedChat = chatState.find((c) => c.id === selectedChatId);

    // Handler for editing a message
    const handleEditMessage = (msg: Message) => {
        setEditingMessageId(msg.id);
        setMessageInput(msg.text);
    };

    // Handler for sending or editing a message
    const handleSend = () => {
    };

    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <SideBar
                chats={chatState}
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-[rgb(var(--sidebar))]">
                <Navbar />

                <div className="flex-1 flex flex-col p-6 pb-1 overflow-y-auto">
                    {selectedChat ? (
                        <MessagesList
                            messages={selectedChat.messages}
                            onEdit={handleEditMessage}
                        />
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-[rgb(var(--muted-foreground))]">
                            <p className="text-lg">Select a chat to start messaging</p>
                        </div>
                    )}
                </div>

                {/* Message Input */}
                {selectedChat && (
                    <MessagesInput
                        value={messageInput}
                        setValue={setMessageInput}
                        onSend={handleSend}
                        isEditing={!!editingMessageId}
                        cancelEdit={() => { setEditingMessageId(null); setMessageInput(""); }}
                    />
                )}
            </div>
        </div>
    );
}