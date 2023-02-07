import { createContext, useState, useContext } from "react";

// Create context
const MachinesContext = createContext({});

// Create custom hook
export function useMachines() {
  return useContext(MachinesContext);
}

// Create provider
export const MachinesProvider = ({ children }) => {
  const [machines, setMachines] = useState([]);

  return (
    <MachinesContext.Provider value={{ machines, setMachines }}>
      {children}
    </MachinesContext.Provider>
  );
};

export default MachinesContext;
