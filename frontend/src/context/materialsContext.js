import { createContext, useState, useContext } from "react";

// Create context
const MaterialsContext = createContext({});

// Create custom hook
export function useMaterials() {
  return useContext(MaterialsContext);
}

// Create provider
export const MaterialsProvider = ({ children }) => {
  const [materials, setMaterials] = useState([]);

  return (
    <MaterialsContext.Provider value={{ materials, setMaterials }}>
      {children}
    </MaterialsContext.Provider>
  );
};

export default MaterialsContext;
