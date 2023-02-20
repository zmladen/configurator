import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Styles/Users.module.css";
import { fetchUsers } from "../../services/userService";
import Table from "./components/Table";
import Container from "../Container";
import Button from "../Buttons/Button";
import NavLink from "../Buttons/NavLink";
import ButtonGroup from "../Buttons/ButtonGroup";
import { useUser } from "../../context/userContext";

function Users(props) {
  const navigate = useNavigate();
  const [loader, setLoader] = useState(false);
  const { users, setUsers } = useUser();

  useEffect(() => {
    setLoader(true);

    const getUsers = async () => {
      const { data } = await fetchUsers();
      setUsers(data.users);
    };

    getUsers();
    setLoader(false);
  }, [users.length]);

  return (
    <div className={styles.Users}>
      <Container>
        <h1>Users</h1>

        <p>{`Total ${users.length} users.`}</p>
        <Table />
        <ButtonGroup>
          <NavLink className="btn btn-dark btn-lg" to={`/users/user/${"new user"}`}>
            Add New User
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
