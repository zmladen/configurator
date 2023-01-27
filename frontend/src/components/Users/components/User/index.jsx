import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Container from "../../../Container";
import Button from "../../../Button";
import styles from "./Styles/User.module.css";
import { useUser } from "../../../../context/userContext";
import { UserIcon } from "@heroicons/react/24/solid";

function User(props) {
  const navigate = useNavigate();
  const { users, setUsers } = useUser();
  const [user, setUser] = useState({});
  const [id, setId] = useState(useParams().id);

  useEffect(() => {
    setUser(users.find((item) => item.id === id));
  }, [id]);

  return (
    <Container>
      <div className={styles.User}>
        <div className={styles.Image}>
          <UserIcon />
        </div>
        <div className={styles.Infos}>
          <p>
            <strong>First Name:</strong> {user?.firstname}
          </p>
          <p>
            <strong>Last Name:</strong> {user?.lastname}
          </p>
          <p>
            <strong>Username:</strong> {user?.username}
          </p>
          <p>
            <strong>Email:</strong> {user?.email}
          </p>
          <p>
            <strong>Admin:</strong> {user?.admin ? "Yes" : "No"}
          </p>
          <p>
            <strong>Status:</strong> {user?.status}
          </p>
          <p>
            <strong>Created:</strong> {user?.created}
          </p>
          <p>
            <strong>Mobile Phone:</strong> {user?.telephone?.mobile}
          </p>
          <p>
            <strong>Office Phone:</strong> {user?.telephone?.office}
          </p>
        </div>
      </div>
      <br />
      <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20" type="button" onClick={() => navigate(-1)}>
        Go Back
      </Button>
    </Container>
  );
}

export default User;
