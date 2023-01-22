import React, { useState } from "react";
import Button from "../../../Button";
import ButtonGroup from "../../../ButtonGroup";
import Modal from "../../../Modal";
import { TrashIcon, PencilIcon } from "@heroicons/react/24/solid";
import styles from "./styles/Table.module.css";

const Table = ({ users }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");

  return (
    <>
      <Modal
        title={modalTitle}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      >
        <ButtonGroup>
          <Button
            className={"btn btn-red pt-5 pb-5"}
            onClick={() => {
              alert("User will be deleted");
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
            <tr key={index}>
              <td>{`${index + 1}.`}</td>
              <td>{user.firstname}</td>
              <td>{user.lastname}</td>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td className={user.admin ? styles.green : styles.red}>
                {user.admin ? "True" : "False"}
              </td>
              <td className={user.status ? styles.green : styles.red}>
                {user.status ? "active" : "deactivate"}
              </td>
              <td>{user.created}</td>
              <td>
                {
                  <ButtonGroup>
                    <Button
                      className={"btn btn-blue pt-5 pb-5"}
                      onClick={() => {
                        alert("User edit clicked...");
                      }}
                    >
                      <PencilIcon />
                      Edit
                    </Button>
                    <Button
                      className={"btn btn-red pt-5 pb-5"}
                      onClick={() => {
                        setIsModalOpen(true);
                        setModalTitle(
                          `Are you sure you want to delete "${user.username}"?`
                        );
                      }}
                    >
                      <TrashIcon />
                      Delete
                    </Button>
                  </ButtonGroup>
                }
              </td>

              {/* <td>
              {user.telephone.mobile} {user.telephone.office}
            </td> */}
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
};

export default Table;
