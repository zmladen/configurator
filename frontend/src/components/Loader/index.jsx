import React, { useState, useEffect } from "react";
import styles from "./Styles/Loader.module.css";
import Logo from "../Logo";

function Loader() {
  const [headerHeight, setHeaderHeight] = useState(0);

  useEffect(() => {
    const header = document.querySelector("#header");
    setHeaderHeight(header.offsetHeight);
    console.log(header.offsetHeight);
  }, []);

  return (
    <div className={styles.loader}>
      <div className={styles.spinner}>
        <Logo src={"./images/tanneLogoHorizontal.svg"} alt="" to="/" />
      </div>
    </div>
  );
}

export default Loader;
