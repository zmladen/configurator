import { createContext, useState, useContext } from "react";

// Create context
const PartsContext = createContext({});

// Create custom hook
export function useParts() {
  return useContext(PartsContext);
}

// Create provider
export const PartsProvider = ({ children }) => {
  const [parts, setParts] = useState([]);

  return (
    <PartsContext.Provider value={{ parts, setParts }}>
      {children}
    </PartsContext.Provider>
  );
};

export default PartsContext;
