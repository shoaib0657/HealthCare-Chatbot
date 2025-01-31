import { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Clock, FileText, PlusCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { chatApi } from '@/api.js';

const History = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedPatient, setSelectedPatient] = useState('');
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [patientHistory, setPatientHistory] = useState('');
  const [doctorNote, setDoctorNote] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handlePatientInput = async (e) => {
    setSelectedPatient(e.target.value);
  };

  const fetchPatientHistory = async () => {
    if (!selectedPatient.trim()) return;
    setPatientHistory('');
    try {
      const history = await chatApi.getPatientHistorySummary(selectedPatient);
      setPatientHistory(history);
      setMessages([]);
    } catch (error) {
      console.error('Error fetching patient history:', error);
      toast.error('Failed to load patient history. Please check the patient ID and try again.');
    }
  };

  const handleAddNote = async () => {
    if (!doctorNote.trim() || !selectedPatient){
      toast.error('Please enter a note and select a patient.');
      return;
    }

    try {
      await chatApi.addMedicalRecord({
        patient_id: parseInt(selectedPatient),
        note: doctorNote,
        provider_id: 1,
      })
      await fetchPatientHistory();
      setDoctorNote('');
      toast.success('Note added successfully.');
    } catch (error) {
      console.error('Error adding doctor note:', error);
      toast.error('Failed to add note. Please try again later.');
    }
  }

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
      toast.error('Error sending message. Please try again later.');
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
        <div className="flex gap-2">
            <input
              type="text"
              value={selectedPatient}
              onChange={handlePatientInput}
              onKeyUp={(e) => {
                if (e.key === 'Enter' && selectedPatient.trim()) {
                  fetchPatientHistory();
                } 
              }}
              placeholder="Enter patient ID"
              className="p-2 border rounded-lg flex-grow"
            />
            <button
              onClick={fetchPatientHistory}
              disabled={!selectedPatient.trim()}
              className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Load History
            </button>
          </div>
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

            {/* Add Doctor's Note */}
            <div className="mt-4 space-y-2">
              {/* <input
                type="text"
                value={providerId}
                onChange={(e) => setProviderId(e.target.value)}
                placeholder="Your Provider ID"
                className="w-full p-2 border rounded"
              /> */}
              <textarea
                value={doctorNote}
                onChange={(e) => setDoctorNote(e.target.value)}
                placeholder="Enter new medical note..."
                className="w-full p-2 border rounded"
                rows="4"
              />
              <button
                onClick={handleAddNote}
                disabled={!selectedPatient || !doctorNote.trim()}
                className="w-full p-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PlusCircle className="w-5 h-5 inline-block mr-1" /> 
                Add Note
              </button>
            </div>

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

      <ToastContainer
        position="bottom-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
};

export default History;