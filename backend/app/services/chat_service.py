from typing import Optional
import uuid
from typing_extensions import Annotated, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from services.patient_service import PatientService

class State(TypedDict):
    patient_id: Optional[int] = None
    patient_history: Optional[str] = None
    thread_id: Optional[str] = None
    messages: Annotated[list, add_messages]

class HealthCareAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")
        self.patient_service = PatientService()

        # Initialize conversation states (replacing checkpointer)
        self.conversation_states = {}

        # Build graph
        self.graph = self._build_graph()

    def call_model(self, state: State):
        """Call the model with the given state."""

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a clinical decision support assistant providing concise, evidence-based medical insights. Your responses should be:
            1. Brief and clinically focused
            2. Prioritizing key diagnostic and treatment considerations

            Context:
            - Patient ID: {patient_id}
            - Medical History: {patient_history}

            Response Format:
            - Use standard medical terminology without explanations
            - Prioritize differential diagnoses and treatment options
            - Lead with critical findings or concerns
            - Include relevant clinical guidelines and criteria
            - Document recommendations in SOAP format when applicable

            Critical Findings Protocol:
            Flag life-threatening conditions with "CRITICAL ALERT" prefix and list immediate action items."""),
            MessagesPlaceholder(variable_name="messages"),
        ])

        messages = state.get("messages", [])
        patient_id = state.get("patient_id", "")
        patient_history = state.get("patient_history", "")

        prompt = prompt_template.invoke({"messages": messages, "patient_id": patient_id, "patient_history": patient_history})

        response = self.llm.invoke(prompt)

        return {"messages": [response]}

    def _build_graph(self):
        workflow = StateGraph(state_schema=State)

        workflow.add_node("model", self.call_model)
        workflow.add_edge(START, "model")

        return workflow.compile()
    
    def process_message(
            self,
            input_text: str,
            patient_id: int,
            thread_id: Optional[str] = None,
    ):
        """Process a message from a user."""

        # Validate input text before processing
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")
        
        # Create or use thread ID
        thread_id = thread_id or str(uuid.uuid4())

        # If a conversation state already exists for this thread, retrieve it.
        # Otherwise, initialize a new state.
        if thread_id in self.conversation_states:
            state = self.conversation_states[thread_id]
        else:    
            history = self.patient_service.get_patient_history(patient_id)
            patient_history = self.patient_service.format_get_patient_history(history)

            # Initialize state
            state = State(
                thread_id=thread_id,
                patient_id=patient_id,
                patient_history=patient_history,
                messages=[]
            )

        # Add input message as HumanMessage object
        input_message = HumanMessage(content=input_text)
        state["messages"].append(input_message)

        # Process through graph
        result = self.graph.invoke(state)

        # Store state in conversation states
        self.conversation_states[thread_id] = result

        # print("result\n", result)

        return self._format_response(result)
    
    def _format_response(self, result):
        """Format the response from the graph."""
        if not result or "messages" not in result:
            raise ValueError("Invalid result from graph.")
        
        # Get the last message
        response = result["messages"][-1].content if result["messages"] else ""

        # print("response\n", response)

        return response
    
    def get_conversation_history(self, thread_id: str):
        """Get the conversation history for a given thread ID."""
        if thread_id not in self.conversation_states:
            raise ValueError("Invalid thread ID.")
        
        return self.conversation_states.get(thread_id, {}).get("messages", [])


    def get_patient_history_summary(self, patient_id: int):
        """Get the patient history summary."""

        history = self.patient_service.get_patient_history(patient_id)
        patient_history = self.patient_service.format_get_patient_history(history)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant summarizing patient histories for doctors. 

            Given the patient history for patient ID {patient_id}, generate a **brief and clinically relevant** summary that highlights only the **most essential** details. 

            Patient History:
            {patient_history}

            **Summary Format (Keep it Short & Focused):**  
            - **Key Conditions:** (Only major chronic illnesses or acute conditions)  
            - **Critical Past Procedures:** (Only if highly relevant)  
            - **Current Medications & Allergies:** (Mention if significant)  
            - **Recent Major Health Changes:** (New symptoms, worsening conditions)  
            - **Urgent Follow-ups or Tests:** (If any)  

            ⚠️ Keep the summary under **5-6 lines** while ensuring clarity and clinical relevance.
            """)
        ])


        prompt = prompt_template.invoke({"patient_id": patient_id, "patient_history": patient_history})

        response = self.llm.invoke(prompt)

        return response.content