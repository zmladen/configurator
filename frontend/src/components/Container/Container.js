import React from "react";
import styles from "./Styles/Container.module.css";

const Container = (props) => (
  <div className={styles.Container}>{props.children}</div>
);
export default Container;
