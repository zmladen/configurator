import React from "react";
import styles from "./Styles/Logo.module.css";
import { NavLink } from "react-router-dom";

const Container = ({ src, alt, to }) =>
  to ? (
    <NavLink to={to} className={styles.Logo}>
      <img src={src} alt={alt}></img>
    </NavLink>
  ) : (
    <img src={src} alt={alt}></img>
  );
export default Container;
