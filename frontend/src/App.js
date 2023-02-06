import { Route, Routes } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import Signup from "./components/SignUp";
import LogIn from "./components/LogIn";
import Header from "./components/Header";
import Configurator from "./components/Configurator";
import Users from "./components/Users";
import UserForm from "./components/Users/components/UserForm";
import UserDetail from "./components/Users/components/UserDetail";
import { UserProvider } from "./context/userContext";
import { MaterialsProvider } from "./context/materialsContext";
import { PartsProvider } from "./context/partsContext";

// Middleware warning solution
// https://stackoverflow.com/questions/70469717/cant-load-a-react-app-after-starting-server

function App(props) {
  return (
    <>
      <UserProvider>
        <Header />
        <MaterialsProvider>
          <PartsProvider>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<LogIn />} />
            <Route path="/users" element={<Users />} />
            <Route path="/users/user/:id" element={<UserForm />} />
            <Route path="/users/user_detail/:id" element={<UserDetail />} />
            <Route path="/configurator" element={<Configurator />} />
          </Routes>
          </PartsProvider>
          
        </MaterialsProvider>
      </UserProvider>
    </>
  );
  // return (
  //   <div className={styles.App}>
  //     <header className={styles.AppHeader}>
  //       <p>Hello World</p>
  //     </header>
  //   </div>
  // );
}

export default App;
