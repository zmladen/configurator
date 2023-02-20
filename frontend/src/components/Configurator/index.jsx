import React, { useState, useEffect } from "react";
import { Route, Router } from "react-router-dom";
import Layout from "../Layout";
import Main from "../Layout/components/Main";
import Footer from "../Layout/components/Footer";
import Loader from "../../components/Loader";
import { sideMenu } from "./menu.config.js";
import { useMaterials } from "../../context/materialsContext";
import { useParts } from "../../context/partsContext";
import { useMachine } from "../../context/machineContext";
import styles from "./Styles/Configurator.module.css";

function Configurator() {
  const { materials, setMaterials } = useMaterials();
  const { parts, setParts } = useParts();
  const { machines, setMachines } = useMachine();
  const [loading, setLoading] = useState(false);

  console.log(materials);
  console.log(parts);
  console.log(machines);

  return (
    <>
      {loading ? (
        <Loader />
      ) : (
        <div className={styles.configurator}>
          <header className={styles.header}>
            <h1>
              <strong>BÜHLER MOTOR </strong>CONFIGURATOR
            </h1>
          </header>
          {/* <Layout menuConfig={sideMenu}>
            <Main>
              <p>Page content</p>
            </Main>
            <Footer>
              <p>Footer content</p>
            </Footer>
          </Layout> */}

          {machines.map((m, i) => (
            <p key={i}>{m.name}</p>
          ))}
        </div>
      )}
    </>
  );
}

export default Configurator;
