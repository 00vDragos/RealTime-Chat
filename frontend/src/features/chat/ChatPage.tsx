import SideBar from "./components/layout/SideBar";
import Navbar from "./components/layout/NavBar";
import MessagesList from "./components/ui/MessagesList";
import MessagesInput from "./components/ui/MessagesInput";
import { useChatMessages } from "../../hooks/useChatMessages";
import { useConversations } from "../../hooks/useConversations";

export default function ChatPage() {
    const { conversations, refetch } = useConversations([]);
    const {
        chatsState,
        selectedChatId,
        setSelectedChatId,
        selectedChat,
        messageInput,
        setMessageInput,
        editingMessageId,
        handleEditStart,
        handleSend,
        handleDelete,
        typingParticipants,
    } = useChatMessages(conversations);

    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <SideBar
                chats={chatsState}
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
                onConversationCreated={async () => {
                    // Refresh the conversation list when a new chat is created
                    await refetch();
                }}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-[rgb(var(--sidebar))]">
                <Navbar name={selectedChat?.name} avatar={selectedChat?.avatar ?? null} />

                <div className="flex-1 flex flex-col p-6 pb-1 overflow-y-auto">
                    {selectedChat ? (
                        <MessagesList
                            messages={selectedChat.messages}
                            onEdit={handleEditStart}
                            onDelete={handleDelete}
                        />
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-[rgb(var(--muted-foreground))]">
                            <p className="text-lg">Select a chat to start messaging</p>
                        </div>
                    )}
                </div>

                {/* Message Input */}
                {selectedChat && typingParticipants.length > 0 && (
                    <div className="px-6 pb-2 text-sm text-[rgb(var(--muted-foreground))]">
                        {`${typingParticipants.map((entry) => entry.userName || "Someone").join(", ")} ${typingParticipants.length > 1 ? "are" : "is"} typing...`}
                    </div>
                )}
                {selectedChat && (
                    <MessagesInput
                        value={messageInput}
                        setValue={setMessageInput}
                        onSend={handleSend}
                        isEditing={!!editingMessageId}
                        cancelEdit={() => { setMessageInput(""); }}
                    />
                )}
            </div>
        </div>
    );
}