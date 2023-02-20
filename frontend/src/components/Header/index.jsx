import React from "react";
import styles from "./Styles/Header.module.css";
import Logo from "../Logo";
import NavLink from "../Buttons/NavLink";
import Button from "../Buttons/Button";
import { useUser } from "../../context/userContext";

function Header() {
  const { user, setUser } = useUser();

  return (
    <header id="header" className={styles.Header}>
      <Logo src={"./images/logo.svg"} alt="" to="/" />
      <p className={styles.User}>{user ? `${user.lastname}, ${user.firstname}` : "Please log in..."}</p>
      <div className={styles.ButtonGroup}>
        {user ? (
          <Button
            className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20"
            onClick={() => {
              console.log("Clicked");
              setUser(null);
            }}
          >
            Log Out
          </Button>
        ) : (
          <NavLink className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20" to="/login">
            Log In
          </NavLink>
        )}
        {!user && (
          <NavLink className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20" to="/signup">
            Sign Up
          </NavLink>
        )}
      </div>
    </header>
  );
}
export default Header;
