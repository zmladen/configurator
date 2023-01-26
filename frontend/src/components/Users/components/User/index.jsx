import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Container from "../../../Container";
import Button from "../../../Button";
import styles from "./Styles/User.module.css";

function User({ user }) {
  const navigate = useNavigate();

  const [id, setId] = useState(useParams().id);

  return (
    <div className={styles.Users}>
      <Container>
        <p>{id}</p>
        <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20" type="button" onClick={() => navigate(-1)}>
          Go Back
        </Button>
      </Container>
    </div>
  );
}

export default User;
