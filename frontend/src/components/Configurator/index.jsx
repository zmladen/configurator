import React, { useState, useEffect } from "react";
import { Route, Router } from "react-router-dom";
import Layout from "../Layout";
import Main from "../Layout/components/Main";
import Footer from "../Layout/components/Footer";
import { sideMenu } from "./menu.config.js";
import { fetchMaterials } from "../../services/materialsService";
import { useMaterials } from "../../context/materialsContext";

function Configurator() {
  const { materials, setMaterials } = useMaterials();

  useEffect(() => {
    const getMaterials = async () => {
      await fetchMaterials()
        .then((response) => {
          setMaterials(response.data);
        })
        .catch(({ response }) => {
          console.log(response);
        });
    };

    getMaterials();
  }, []);

  console.log(materials);
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
