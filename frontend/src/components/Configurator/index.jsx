import React, { useState, useEffect } from "react";
import { Route, Router } from "react-router-dom";
import Layout from "../Layout";
import Main from "../Layout/components/Main";
import Footer from "../Layout/components/Footer";
import Loader from "../../components/Loader";
import { sideMenu } from "./menu.config.js";
import { fetchMaterials } from "../../services/materialsService";
import { fetchParts } from "../../services/partsService";
import { useMaterials } from "../../context/materialsContext";
import { useParts } from "../../context/partsContext";

function Configurator() {
  const { materials, setMaterials } = useMaterials();
  const { parts, setParts } = useParts();
  const [loading, setLoading] = useState(true);
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

    const getParts = async () => {
      await fetchParts()
        .then((response) => {
          setParts(response.data);
        })
        .catch(({ response }) => {
          console.log(response);
        });
    };

    getMaterials();
    getParts();
    setTimeout(() => setLoading(false), 1000);
  }, []);

  console.log(materials);
  console.log(parts);

  return (
    <>
      {loading ? (
        <Loader />
      ) : (
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
      )}
    </>
  );
}

export default Configurator;
