import { createContext, useState, useContext } from "react";

// Create context
const MachineContext = createContext({});

// Create custom hook
export function useMachine() {
  return useContext(MachineContext);
}

// Create provider
export const MachineProvider = ({ children }) => {
  const [machines, setMachines] = useState([]);

  return (
    <MachineContext.Provider value={{ machines, setMachines }}>
      {children}
    </MachineContext.Provider>
  );
};

export default MachineContext;
