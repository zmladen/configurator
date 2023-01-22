import React from "react";
import styles from "./Styles/Sidebar.module.css";
import NavItem from "./NavItem/NavItem.jsx";
import Logo from "../../../Logo";

const Sidebar = (props) => {
  return (
    <nav className={styles.Sidebar}>
      <header className={styles.Header}>
        <Logo src={"./images/tanne.svg"} />
        Configurator
      </header>
      {props.menuConfig.map((item, index) => {
        return <NavItem key={`${item.label}-${index}`} item={item} />;
      })}
    </nav>
  );
};

export default Sidebar;
