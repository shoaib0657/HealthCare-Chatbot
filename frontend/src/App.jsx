import {Route, Routes} from "react-router-dom";
import Pinecone from './components/pinecone/Pinecone';
import History from "./pages/History";
import SymptomChecker from "./pages/SymptomChecker";

const App = () => {
  
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<History/>} />
        <Route path="/pinecone"  element={<Pinecone/>} />
        <Route path="/checker" element={<SymptomChecker/>} />
      </Routes>
    </div>
  );
};

export default App;