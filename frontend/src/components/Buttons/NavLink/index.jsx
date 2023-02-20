import React from "react";
import { NavLink } from "react-router-dom";
import styles from "../Styles/Buttons.module.css";

const Container = ({ className, to, children }) => (
  <NavLink
    // {...rest}
    className={
      className &&
      className
        .split(" ")
        .map((item) => `${styles[item]}`)
        .join(" ")
    }
    to={to}
  >
    {children}
  </NavLink>
);
export default Container;
