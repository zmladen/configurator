import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../../Buttons/Button";
import ButtonGroup from "../../../Buttons/ButtonGroup";
import Modal from "../../../Modal";
import { TrashIcon, PencilIcon } from "@heroicons/react/24/solid";
import { deleteUser } from "../../../../services/userService";
import { useUser } from "../../../../context/userContext";

import styles from "./styles/Table.module.css";

const Table = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [user, setUser] = useState({});
  const { users, setUsers } = useUser();

  return (
    <>
      <Modal title={modalTitle} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <ButtonGroup>
          <Button
            className={"btn btn-red pt-5 pb-5"}
            onClick={() => {
              deleteUser(user)
                .then((response) => {
                  console.log(response);
                  setUsers(response.data.data);
                  alert(response.data.message);
                })
                .catch(({ response }) => {
                  alert(response.data);
                });

              setIsModalOpen(false);
            }}
          >
            Yes
          </Button>
          <Button
            className={"btn btn-green pt-5 pb-5"}
            onClick={() => {
              setIsModalOpen(false);
            }}
          >
            No
          </Button>
        </ButtonGroup>
      </Modal>

      <table className={styles.table}>
        <thead>
          <tr>
            <th>Index</th>
            <th>Firstname</th>
            <th>Lastname</th>
            <th>Username</th>
            <th>E-mail</th>
            <th>Admin</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
            {/* <th>telephone</th> */}
          </tr>
        </thead>
        <tbody>
          {users.map((user, index) => (
            <tr
              key={index}
              onClick={(e) => {
                navigate(`user_detail/${user.id}`);
              }}
            >
              <td>{`${index + 1}.`}</td>
              <td>{user.firstname}</td>
              <td>{user.lastname}</td>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td className={user.admin ? styles.green : styles.red}>{user.admin ? "True" : "False"}</td>
              <td className={user.status ? styles.green : styles.red}>{user.status ? "Active" : "Deactive"}</td>
              <td>{user.created}</td>
              <td>
                {
                  <ButtonGroup>
                    <Button
                      className="btn btn-blue"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`user/${user.id}`);
                      }}
                    >
                      <PencilIcon />
                      Edit
                    </Button>
                    <Button
                      className="btn btn-red"
                      onClick={(e) => {
                        e.stopPropagation();

                        setIsModalOpen(true);
                        setUser(user);
                        setModalTitle(`Are you sure you want to delete "${user.username}"?`);
                      }}
                    >
                      <TrashIcon />
                      Delete
                    </Button>
                  </ButtonGroup>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
};

export default Table;
