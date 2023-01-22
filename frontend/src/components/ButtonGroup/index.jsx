import React from "react";
import styles from "./Styles/ButtonGroup.module.css";

function ButtonGroup({ children }) {
  return <div className={styles.ButtonGroup}>{children}</div>;
}

export default ButtonGroup;
