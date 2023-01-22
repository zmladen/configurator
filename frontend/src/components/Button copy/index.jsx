import React from "react";
import styles from "./Styles/Button.module.css";
// https://www.javascriptstuff.com/css-modules-by-example/

const Container = (props) => (
  <button
    onClick={props.onClick}
    className={`${styles.Button} ${
      props.color ? styles[props.color] : "White"
    } ${props.loading ? styles.Loading : ""}`}
  >
    <span className={styles.ButtonText}>{props.children}</span>
  </button>
);
export default Container;
