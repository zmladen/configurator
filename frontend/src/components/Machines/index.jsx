import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
// import Table from "./components/Table";
import Container from "../Container";
import Button from "../Buttons/Button";
import NavLink from "../Buttons/NavLink";
import ButtonGroup from "../Buttons/ButtonGroup";
import { useMachine } from "../../context/machineContext";
import styles from "./Styles/Machines.module.css";

function Users(props) {
  const navigate = useNavigate();
  const { machines, setMachines } = useMachine();

  return (
    <div>
      <Container>
        <h1>Machines</h1>
        <p>{`Total ${machines.length} machines.`}</p>
        {/* <Table /> */}
        <ButtonGroup>
          <NavLink className="btn btn-dark btn-lg" to={`/machines/machine/${"new machine"}`}>
            Add Machine
          </NavLink>
          <Button className="btn btn-dark btn-lg" type="button" onClick={() => navigate(-1)}>
            Cancel
          </Button>
        </ButtonGroup>
      </Container>
    </div>
  );
}

export default Users;
