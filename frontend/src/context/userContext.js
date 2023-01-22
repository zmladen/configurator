import { createContext, useState, useContext } from "react";

// Create context
const UserContext = createContext({});

// Create custom hook
export function useUser() {
  return useContext(UserContext);
}

// Create provider
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export default UserContext;
