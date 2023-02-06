import React from "react";
import styles from "./Styles/Loader.module.css";
import Logo from "../Logo";

const Loader = () => (
  <div className={styles.loader}>
    <div className={styles.spinner}>
      <Logo src={"./images/tanneLogoHorizontal.svg"} alt="" to="/" />

      {/* <div className={styles.bounce1}></div>
      <div className={styles.bounce2}></div>
      <div className={styles.bounce3}></div> */}
    </div>
  </div>
);

export default Loader;
