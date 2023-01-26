import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./Styles/Users.module.css";
import { fetchUsers } from "../../services/userService";
import Table from "./components/Table";
import Container from "../Container";
import Button from "../../components/Button";
import NavLink from "../../components/NavLink";
import ButtonGroup from "../../components/ButtonGroup";
import { useUser } from "../../context/userContext";

function Users(props) {
  const [loader, setLoader] = useState(false);
  const { users, setUsers } = useUser();
  // const navigate = useNavigate();

  useEffect(() => {
    setLoader(true);

    const getUsers = async () => {
      const { data } = await fetchUsers();
      // console.log(data.users);
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
          <NavLink to={`/users/user/${"new user"}`}>Add New User</NavLink>
        </ButtonGroup>
      </Container>
    </div>
  );
}

export default Users;
