import SideBar from "./SideBar";
import Navbar from "./NavBar";
import { useState } from "react";
import MessagesInput from "./MessagesInput";
import { chats } from "./mockData";

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
                        <div className="flex flex-col gap-4">
                            {selectedChat.messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${msg.sender === 'Me' ? 'bg-green-100 self-end' : 'bg-white self-start'}`}
                                >
                                    <div className="font-semibold text-xs text-gray-500 mb-1">{msg.sender}</div>
                                    <div>{msg.text}</div>
                                    <div className="text-xs text-gray-400 mt-1 text-right">{msg.time}</div>
                                </div>
                            ))}
                        </div>
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