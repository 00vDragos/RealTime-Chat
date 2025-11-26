import SideBar from "./components/layout/SideBar";
import { useState } from "react";
import { chats } from "./mockData";
import Navbar from "./components/layout/NavBar";
import MessagesList from "./components/ui/MessagesList";
import MessagesInput from "./components/ui/MessagesInput";


export default function ChatPage() {
    const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
    const selectedChat = chats.find((c) => c.id === selectedChatId);

    return (
        <div className="flex h-screen">
            
            {/* Sidebar */}
            <SideBar
                chats={chats}
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-gray-50">
                <Navbar />

                <div className="flex-1 flex flex-col p-6 overflow-y-auto">
                    {selectedChat ? (
                        <MessagesList messages={selectedChat.messages} />
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-gray-400">
                            <p className="text-lg">Select a chat to start messaging</p>
                        </div>
                    )}
                </div>

                {/* Message Input */}
                {selectedChat && (
                    <MessagesInput />
                )}
                
            </div>
        </div>
    );
}