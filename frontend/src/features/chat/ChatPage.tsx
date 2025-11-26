import SideBar from "./SideBar";
import Navbar from "./NavBar";

export default function ChatPage() {
    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <SideBar />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-gray-50">
                {/* Navbar at the top */}
                <Navbar />
                {/* Placeholder for chat content */}
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center text-gray-400">
                        <p className="text-lg">Select a chat to start messaging</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

