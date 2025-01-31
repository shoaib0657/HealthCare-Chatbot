from typing import Optional
import uuid
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState, StateGraph, START
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from services.patient_service import PatientService

class State(MessagesState):
    patient_id: Optional[int] = None
    patient_history: Optional[str] = None
    thread_id: Optional[str] = None

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
            ("system", """
            You are a healthcare assistant. Please answer all questions professionally 
            and accurately.
            
            Current Patient ID: {patient_id}
            Patient History: {patient_history}
            
            Guidelines:
            - Maintain HIPAA compliance
            - Use medical terminology appropriately
            - Refer to specialists when necessary
            """),
            MessagesPlaceholder(variable_name="messages"),
        ])

        messages = state.get("messages", [])
        patient_id = state.get("patient_id", "")
        patient_history = state.get("patient_history", "")

        prompt = prompt_template.invoke({"messages": messages, "patient_id": patient_id, "patient_history": patient_history})

        response = self.llm.invoke(prompt)

        return {"messages": response}

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

        history = self.patient_service.get_patient_history(patient_id)
        patient_history = self.patient_service.format_get_patient_history(history)

        # Initialize state
        initial_state = State(
            thread_id=thread_id,
            patient_id=patient_id,
            patient_history=patient_history,
            messages=[]
        )

        # Add input message as HumanMessage object
        input_message = HumanMessage(content=input_text)
        initial_state["messages"].append(input_message)

        # Store state in conversation states
        self.conversation_states[thread_id] = initial_state

        # Process through graph
        result = self.graph.invoke(initial_state)

        return self._format_response(result)
    
    def _format_response(self, result):
        """Format the response from the graph."""
        if not result or "messages" not in result:
            raise ValueError("Invalid result from graph.")
        
        # Get the last message
        response = result["messages"][-1].content if result["messages"] else ""

        print("response\n", response)

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
            ("system", """
            Here is the patient history for patient ID {patient_id}:
            {patient_history}
            Summarize the patient's history with the most important details.
            """),
        ])

        prompt = prompt_template.invoke({"patient_id": patient_id, "patient_history": patient_history})

        response = self.llm.invoke(prompt)

        return response.content