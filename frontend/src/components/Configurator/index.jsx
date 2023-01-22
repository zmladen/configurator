import React from "react";
import { Route, Router } from "react-router-dom";
import Layout from "../Layout";
import Main from "../Layout/components/Main";
import Footer from "../Layout/components/Footer";
import { sideMenu } from "./menu.config.js";

function Configurator() {
  console.log("Configurator");
  return (
    <div className="Configurator">
      <Layout menuConfig={sideMenu}>
        <Main>
          <p>Page content</p>
        </Main>
        <Footer>
          <p>Footer content</p>
        </Footer>
      </Layout>
    </div>
  );
}

export default Configurator;
