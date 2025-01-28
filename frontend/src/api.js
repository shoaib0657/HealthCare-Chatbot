// api.js
const API_BASE_URL = 'http://localhost:8000/api';

export const chatApi = {
  // Patient management
  createPatient: async (patientData) => {
    const response = await fetch(`${API_BASE_URL}/patients`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patientData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  getPatient: async (patientId) => {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  // Medical records management
  addMedicalRecord: async (recordData) => {
    const response = await fetch(`${API_BASE_URL}/medical-records`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(recordData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  deleteMedicalRecord: async (recordId) => {
    const response = await fetch(`${API_BASE_URL}/medical-records/${recordId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  // Chat functionality
  sendMessage: async (message, patientId, threadId) => {

    console.log(message, patientId, threadId);

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        patient_id: patientId,
        thread_id: threadId,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  getChatHistory: async (threadId) => {
    const response = await fetch(`${API_BASE_URL}/chat/${threadId}/history`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },

  getPatientHistory: async (patientId) => {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}/history`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  },
};

// updata database api
export const updateDatabaseApi = {
  updateDatabase: async (indexname, namespace) => {
    const response = await fetch(`${API_BASE_URL}/updatedatabase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ indexname, namespace }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return response.json();
  },
};