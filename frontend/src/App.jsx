// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App


import { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Clock, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { chatApi } from '@/api.js';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [patientHistory, setPatientHistory] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Mock patient data - replace with actual API calls
  const patients = [
    { id: 1, name: "John Doe" },
    { id: 2, name: "Jane Smith" },
    { id: 3, name: "Bob Johnson" }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handlePatientSelect = async (patientId) => {
    setSelectedPatient(patientId);
    const history = await chatApi.getPatientHistory(patientId);
    setPatientHistory(history);
    // setPatientHistory("Patient history will be displayed here");
    setMessages([]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedPatient) return;

    setLoading(true);

    try {
      const response = await chatApi.sendMessage(inputMessage, selectedPatient, currentThreadId);
      // Add the user's message to the chat
      const userMessage = {
        content: inputMessage,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };

      // Add the assistant's response
      const assistantMessage = {
        content: response.message,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage, assistantMessage]);
      setCurrentThreadId(response.thread_id);
      setInputMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[100vh] w-[100vw] mx-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Healthcare Assistant</CardTitle>
        </CardHeader>
        <CardContent>
          <Select onValueChange={handlePatientSelect}>
            <SelectTrigger>
              <SelectValue placeholder="Select a patient" />
            </SelectTrigger>
            <SelectContent>
              {patients.map(patient => (
                <SelectItem key={patient.id} value={patient.id}>
                  {patient.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <div className="grid grid-cols-3 gap-4 flex-grow">
        {/* Patient History Sidebar */}
        <Card className="col-span-1 overflow-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Patient History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{patientHistory}</p>
          </CardContent>
        </Card>

        {/* Chat Area */}
        <Card className="col-span-2 flex flex-col">
          <CardHeader>
            <CardTitle>Conversation</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col">
            {/* Messages Container */}
            <div className="flex-grow overflow-auto mb-4 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-2 ${message.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                >
                  {message.sender === 'assistant' && (
                    <Bot className="w-6 h-6 mt-1 text-blue-500" />
                  )}
                  <div
                    className={`rounded-lg p-3 max-w-[80%] ${message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100'
                      }`}
                  >
                    <p>{message.content}</p>
                    <div className="flex items-center gap-1 mt-1 text-xs opacity-70">
                      <Clock className="w-3 h-3" />
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  {message.sender === 'user' && (
                    <User className="w-6 h-6 mt-1 text-blue-500" />
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-gray-500">
                  <Bot className="w-6 h-6" />
                  <span>Thinking...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex gap-2 mt-auto">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message..."
                className="flex-grow p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!selectedPatient || loading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!selectedPatient || !inputMessage.trim() || loading}
                className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default App;