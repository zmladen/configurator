import React, { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import styles from "./Styles/NavItem.module.css";
import { ChevronDownIcon } from "@heroicons/react/24/solid";

const resolveLinkPath = (childTo, parentTo) => `${parentTo}/${childTo}`;

const NavItemHeader = (props) => {
  const { item } = props;
  const { label, Icon, to: headerToPath, children } = item;
  const location = useLocation();

  const [expanded, setExpand] = useState(
    location.pathname.includes(headerToPath)
  );

  const onExpandChange = (e) => {
    e.preventDefault();
    setExpand((expanded) => !expanded);
  };

  return (
    <>
      <button
        className={`${styles.navItem} ${styles.navItemHeaderButton}`}
        onClick={onExpandChange}
      >
        <Icon className={styles.navIcon} />
        <span className={styles.navLabel}>{label}</span>
        <ChevronDownIcon
          className={`${styles.navItemHeaderChevron} ${
            expanded && styles.chevronExpanded
          }`}
        />
      </button>

      {expanded && (
        <div className={styles.navChildrenBlock}>
          {children.map((item, index) => {
            const key = `${item.label}-${index}`;

            const { label, Icon, children } = item;

            if (children) {
              return (
                <div key={key}>
                  <NavItemHeader
                    item={{
                      ...item,
                      to: resolveLinkPath(item.to, props.item.to),
                    }}
                  />
                </div>
              );
            }

            return (
              <NavLink
                key={key}
                to={resolveLinkPath(item.to, props.item.to)}
                className={styles.navItem}
                // activeClassName={styles.activeNavItem}
              >
                <Icon className={styles.navIcon} />
                <span className={styles.navLabel}>{label}</span>
              </NavLink>
            );
          })}
        </div>
      )}
    </>
  );
};

export default NavItemHeader;
