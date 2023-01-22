import React from "react";
import { NavLink } from "react-router-dom";
import styles from "./Styles/NavLink.module.css";

const Container = (props) => (
  <NavLink className={styles.NavLink} to={props.to}>
    {props.children}
  </NavLink>
);
export default Container;
