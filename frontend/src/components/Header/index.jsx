import React from "react";
import styles from "./Styles/Header.module.css";
import Logo from "../Logo";
import NavLink from "../NavLink";
import Button from "../Button";
import { useUser } from "../../context/userContext";

function Header() {
  const { user, setUser } = useUser();

  return (
    <header className={styles.Header}>
      <Logo src={"./images/logo.svg"} alt="" to="/" />
      <p className={styles.User}>
        {user ? `${user.lastname}, ${user.firstname}` : "Please log in..."}
      </p>
      <div className={styles.ButtonGroup}>
        {user ? (
          <Button
            className="btn btn-navlink mr-5"
            onClick={() => {
              console.log("Clicked");
              setUser(null);
            }}
          >
            Log Out
          </Button>
        ) : (
          <NavLink to="/login">Log In</NavLink>
        )}
        {!user && <NavLink to="/signup">Sign Up</NavLink>}
      </div>
    </header>
  );
}
export default Header;
