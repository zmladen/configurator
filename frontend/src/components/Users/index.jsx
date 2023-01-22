import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Styles/Users.module.css";
import { fetchUsers } from "../../services/userService";
import Table from "./components/Table";
import Container from "../Container/Container";
import Button from "../../components/Button";

function Users(props) {
  const [loader, setLoader] = useState(false);
  const [users, setUsers] = useState([]);
  // const navigate = useNavigate();

  useEffect(() => {
    setLoader(true);

    const getUsers = async () => {
      const { data } = await fetchUsers();
      setUsers(data.users);
    };

    getUsers();
    setLoader(false);
  }, []);

  return (
    <div className={styles.Users}>
      <Container>
        <h1>Users</h1>
        <p>{`Total ${users.length} users.`}</p>
        <Table users={users} />
        <Button className="btn btn-dark btn-lg pt-10 pb-10 pl-20 pr-20 mt-5 br-50">
          Add New User
        </Button>
      </Container>
    </div>
  );
}

export default Users;
