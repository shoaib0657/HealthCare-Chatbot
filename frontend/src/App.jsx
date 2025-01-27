import {Route, Routes} from "react-router-dom";
import Pinecone from './components/pinecone/Pinecone';
import History from "./pages/History";

const App = () => {
  
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<History/>} />
        <Route path="/pinecone"  element={<Pinecone/>} />
      </Routes>
    </div>
  );
};

export default App;