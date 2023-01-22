import React from "react";
import { NavLink } from "react-router-dom";
import styles from "./Styles/NavItem.module.css";
import NavItemHeader from "./NavItemHeader.jsx";

const NavItem = (props) => {
  const { label, Icon, to, children } = props.item;

  if (children) {
    return <NavItemHeader item={props.item} />;
  }

  return (
    <NavLink end to={to} className={styles.navItem}>
      <Icon className={styles.navIcon} />
      <span className={styles.navLabel}>{label}</span>
    </NavLink>
  );
};

export default NavItem;
