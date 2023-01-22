import React from "react";
import style from "./Styles/Layout.module.css";
import Sidebar from "./components/sidebar";
import Main from "./components/Main";
import Footer from "./components/Footer";

const Layout = (props) => {
  const { children } = props;

  return (
    <div className={style.layout}>
      {/* <header className={style.header}></header> */}
      <aside className={style.aside}>
        <Sidebar menuConfig={props.menuConfig || {}} />
      </aside>
      <main className={style.main}>
        {children.filter((child) => child.type === Main)}
      </main>
      <footer className={style.footer}>
        {children.filter((child) => child.type === Footer)}
      </footer>
    </div>
  );
};

export default Layout;
